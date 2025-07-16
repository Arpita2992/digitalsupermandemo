"""
File processor utility to handle various file formats with performance optimizations
"""

import os
import json
import xml.etree.ElementTree as ET
import base64
import io
import zipfile
import tempfile
import hashlib
import time
from typing import Dict, Any, Optional, List, Union
from functools import lru_cache
from PIL import Image
import PyPDF2
from utils.performance import perf_monitor, cache_result, measure_execution_time

class FileProcessor:
    def __init__(self):
        self.supported_formats = {
            '.png': self._process_image,
            '.jpg': self._process_image,
            '.jpeg': self._process_image,
            '.gif': self._process_image,
            '.bmp': self._process_image,
            '.tiff': self._process_image,
            '.webp': self._process_image,
            '.pdf': self._process_pdf,
            '.xml': self._process_xml,
            '.drawio': self._process_drawio,
            '.vsdx': self._process_vsdx,
            '.svg': self._process_svg,
            '.txt': self._process_text,
            '.json': self._process_json
        }
        
        # Performance settings
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.cache_ttl = 3600  # 1 hour
        
        # File content cache
        self._file_cache = {}
        self._max_cache_size = 50  # Increased cache size
    
    def _get_file_cache_key(self, filepath):
        """Generate cache key based on file path and modification time"""
        try:
            stat = os.stat(filepath)
            return hashlib.md5(f"{filepath}{stat.st_mtime}{stat.st_size}".encode()).hexdigest()
        except OSError:
            return hashlib.md5(f"{filepath}{time.time()}".encode()).hexdigest()
    
    def _get_from_cache(self, cache_key):
        """Get cached file content"""
        return self._file_cache.get(cache_key)
    
    def _save_to_cache(self, cache_key, content):
        """Save file content to cache with LRU eviction"""
        if len(self._file_cache) >= self._max_cache_size:
            # Remove oldest entry (simple LRU)
            oldest_key = next(iter(self._file_cache))
            del self._file_cache[oldest_key]
        self._file_cache[cache_key] = content

    @measure_execution_time
    def process_file(self, filepath: str) -> str:
        """Process uploaded file and extract relevant content with caching"""
        try:
            # Validate file
            self._validate_file(filepath)
            
            file_extension = os.path.splitext(filepath)[1].lower()
            
            if file_extension not in self.supported_formats:
                raise ValueError(f'Unsupported file format: {file_extension}')
            
            # Check cache first
            cache_key = self._get_file_cache_key(filepath)
            cached_content = self._get_from_cache(cache_key)
            if cached_content:
                print(f"🚀 File Processor: Using cached content for {os.path.basename(filepath)}")
                return cached_content
            
            # Process file based on extension
            processor = self.supported_formats[file_extension]
            result = processor(filepath)
            
            # Extract text content based on result type
            if isinstance(result, dict):
                content = result.get('text', '')
                if result.get('type') == 'image' and 'image_path' in result:
                    # For images, create enhanced content for AI processing
                    content = self._create_image_analysis_content(filepath, result)
            else:
                content = str(result)
            
            # Save to cache
            self._save_to_cache(cache_key, content)
            
            return content
            
        except Exception as e:
            print(f"❌ File Processor Error: {str(e)}")
            raise ValueError(f'Error processing file: {str(e)}')
    
    def _validate_file(self, filepath: str) -> None:
        """Validate file exists and is within size limits"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        file_size = os.path.getsize(filepath)
        if file_size > self.max_file_size:
            raise ValueError(f"File too large: {file_size:,} bytes (max: {self.max_file_size:,} bytes)")
        
        if file_size == 0:
            raise ValueError("File is empty")
    
    def _create_image_analysis_content(self, filepath: str, result: Dict[str, Any]) -> str:
        """Create enhanced content for image analysis"""
        try:
            with Image.open(filepath) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Get image info
                width, height = img.size
                format_name = img.format or 'Unknown'
                
                # Convert to base64 for AI processing
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG', optimize=True)
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                
                # Create enhanced prompt for architecture analysis
                content = f"""
ARCHITECTURE DIAGRAM ANALYSIS REQUEST

Image Details:
- Format: {format_name}
- Dimensions: {width}x{height}
- File: {os.path.basename(filepath)}

Base64 Image Data:
{img_base64}

ANALYSIS INSTRUCTIONS:
Please analyze this architecture diagram and identify:
1. Azure services and components
2. Data flow and connections
3. Architecture patterns
4. Security boundaries
5. Network topology
6. Resource groups and subscriptions
7. Any compliance or policy considerations

Focus specifically on Azure services and provide detailed component analysis.
"""
                
                return content.strip()
        except Exception as e:
            return f"Error creating image analysis content: {str(e)}"
    
    @lru_cache(maxsize=32)
    def _process_image(self, filepath: str) -> Dict[str, Any]:
        """Process image files with caching"""
        try:
            with Image.open(filepath) as img:
                # Extract image metadata
                metadata = {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode
                }
                
                # Try to extract EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    metadata['exif'] = dict(img._getexif())
                
                return {
                    'type': 'image',
                    'text': f'Image file: {img.format} format, {img.width}x{img.height} pixels',
                    'metadata': metadata,
                    'image_path': filepath
                }
        except Exception as e:
            return {
                'type': 'image',
                'text': f'Error processing image: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    @lru_cache(maxsize=16)
    def _process_pdf(self, filepath: str) -> Dict[str, Any]:
        """Process PDF files with caching"""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                text_content = []
                for page_num, page in enumerate(pdf_reader.pages):
                    text_content.append(f"Page {page_num + 1}: {page.extract_text()}")
                
                metadata = {
                    'num_pages': len(pdf_reader.pages),
                    'title': pdf_reader.metadata.get('/Title', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    'author': pdf_reader.metadata.get('/Author', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    'creator': pdf_reader.metadata.get('/Creator', 'Unknown') if pdf_reader.metadata else 'Unknown'
                }
                
                return {
                    'type': 'pdf',
                    'text': '\n'.join(text_content),
                    'metadata': metadata
                }
        except Exception as e:
            return {
                'type': 'pdf',
                'text': f'Error processing PDF: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    @lru_cache(maxsize=32)
    def _process_xml(self, filepath: str) -> Dict[str, Any]:
        """Process XML files with enhanced parsing and caching"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parse XML
            root = ET.fromstring(content)
            
            # Extract text content and structure
            text_content = self._extract_xml_text(root)
            
            metadata = {
                'root_tag': root.tag,
                'namespace': root.tag.split('}')[0][1:] if '}' in root.tag else None,
                'element_count': len(list(root.iter()))
            }
            
            return {
                'type': 'xml',
                'text': text_content,
                'metadata': metadata,
                'xml_content': content
            }
        except Exception as e:
            return {
                'type': 'xml',
                'text': f'Error processing XML: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    @lru_cache(maxsize=16)
    def _process_drawio(self, filepath: str) -> Dict[str, Any]:
        """Process Draw.io files with enhanced extraction and caching"""
        try:
            # Try to process as compressed first
            try:
                with zipfile.ZipFile(filepath, 'r') as zip_file:
                    diagram_files = [f for f in zip_file.namelist() if f.endswith('.xml')]
                    
                    if diagram_files:
                        main_diagram = diagram_files[0]
                        with zip_file.open(main_diagram) as xml_file:
                            xml_content = xml_file.read().decode('utf-8')
                        
                        root = ET.fromstring(xml_content)
                        text_content = self._extract_drawio_content(root)
                        
                        metadata = {
                            'diagram_files': diagram_files,
                            'main_diagram': main_diagram,
                            'is_compressed': True
                        }
                        
                        return {
                            'type': 'drawio',
                            'text': text_content,
                            'metadata': metadata,
                            'xml_content': xml_content
                        }
            except zipfile.BadZipFile:
                pass
            
            # Process as uncompressed XML
            return self._process_xml(filepath)
            
        except Exception as e:
            return {
                'type': 'drawio',
                'text': f'Error processing Draw.io file: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    @lru_cache(maxsize=8)
    def _process_vsdx(self, filepath: str) -> Dict[str, Any]:
        """Process Visio files with caching"""
        try:
            with zipfile.ZipFile(filepath, 'r') as zip_file:
                # Look for content files
                content_files = [f for f in zip_file.namelist() if 'content' in f.lower()]
                
                extracted_content = []
                for content_file in content_files:
                    try:
                        with zip_file.open(content_file) as cf:
                            content = cf.read().decode('utf-8')
                            extracted_content.append(content)
                    except:
                        continue
                
                metadata = {
                    'content_files': content_files,
                    'file_count': len(zip_file.namelist())
                }
                
                return {
                    'type': 'vsdx',
                    'text': '\n'.join(extracted_content),
                    'metadata': metadata
                }
        except Exception as e:
            return {
                'type': 'vsdx',
                'text': f'Error processing VSDX file: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    @lru_cache(maxsize=32)
    def _process_svg(self, filepath: str) -> Dict[str, Any]:
        """Process SVG files with enhanced text extraction and caching"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parse SVG
            root = ET.fromstring(content)
            
            # Extract text content
            text_content = self._extract_svg_text(root)
            
            # Extract SVG metadata
            metadata = {
                'width': root.get('width', 'Unknown'),
                'height': root.get('height', 'Unknown'),
                'viewBox': root.get('viewBox', 'Unknown'),
                'element_count': len(list(root.iter()))
            }
            
            return {
                'type': 'svg',
                'text': text_content,
                'metadata': metadata,
                'svg_content': content
            }
        except Exception as e:
            return {
                'type': 'svg',
                'text': f'Error processing SVG: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    @lru_cache(maxsize=32)
    def _process_text(self, filepath: str) -> Dict[str, Any]:
        """Process text files with enhanced encoding support"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            content = None
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as file:
                        content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                raise ValueError("Could not decode text file with any supported encoding")
            
            metadata = {
                'line_count': len(content.splitlines()),
                'char_count': len(content),
                'encoding': encoding
            }
            
            return {
                'type': 'text',
                'text': content,
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'type': 'text',
                'text': f'Error processing text file: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    @lru_cache(maxsize=16)
    def _process_json(self, filepath: str) -> Dict[str, Any]:
        """Process JSON files with caching"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            
            # Format JSON for analysis
            formatted_json = json.dumps(json_data, indent=2)
            
            metadata = {
                'keys': list(json_data.keys()) if isinstance(json_data, dict) else [],
                'size': len(formatted_json),
                'type': type(json_data).__name__
            }
            
            return {
                'type': 'json',
                'text': formatted_json,
                'metadata': metadata,
                'json_data': json_data
            }
            
        except json.JSONDecodeError as e:
            return {
                'type': 'json',
                'text': f'Invalid JSON file: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
        except Exception as e:
            return {
                'type': 'json',
                'text': f'Error processing JSON file: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    def _extract_xml_text(self, element) -> str:
        """Extract text content from XML element with better formatting"""
        text_parts = []
        
        # Add element tag and attributes
        if element.tag:
            tag_name = element.tag.split('}')[-1] if '}' in element.tag else element.tag
            text_parts.append(f"Element: {tag_name}")
        
        if element.attrib:
            for attr, value in element.attrib.items():
                text_parts.append(f"  {attr}: {value}")
        
        # Add text content
        if element.text and element.text.strip():
            text_parts.append(f"  Text: {element.text.strip()}")
        
        # Recursively process children
        for child in element:
            child_text = self._extract_xml_text(child)
            if child_text:
                text_parts.append(f"  {child_text}")
        
        return '\n'.join(text_parts)
    
    def _extract_drawio_content(self, root) -> str:
        """Extract content from Draw.io XML with enhanced parsing"""
        text_parts = ["Draw.io Architecture Diagram:"]
        
        # Look for mxCell elements which contain the diagram content
        for cell in root.iter():
            if 'mxCell' in cell.tag:
                # Extract cell value (component name)
                value = cell.get('value', '')
                if value and value.strip():
                    # Decode HTML entities
                    value = self._decode_html_entities(value)
                    text_parts.append(f"  Component: {value}")
                
                # Extract style information
                style = cell.get('style', '')
                if style and ('azure' in style.lower() or 'aws' in style.lower()):
                    text_parts.append(f"  Style: {style}")
        
        return '\n'.join(text_parts)
    
    def _extract_svg_text(self, element) -> str:
        """Extract text content from SVG element with enhanced extraction"""
        text_parts = []
        
        # Look for text elements
        for text_elem in element.iter():
            tag_name = text_elem.tag.split('}')[-1] if '}' in text_elem.tag else text_elem.tag
            
            if tag_name in ['text', 'tspan', 'title', 'desc']:
                if text_elem.text and text_elem.text.strip():
                    text_parts.append(f"[{tag_name}] {text_elem.text.strip()}")
        
        return '\n'.join(text_parts)
    
    def _decode_html_entities(self, text: str) -> str:
        """Decode common HTML entities"""
        entities = {
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' '
        }
        
        for entity, replacement in entities.items():
            text = text.replace(entity, replacement)
        
        return text
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_file_info(self, filepath: str) -> Dict[str, Union[str, int]]:
        """Get file information"""
        try:
            stat = os.stat(filepath)
            return {
                'filename': os.path.basename(filepath),
                'size': stat.st_size,
                'extension': os.path.splitext(filepath)[1].lower().lstrip('.'),
                'modified': stat.st_mtime
            }
        except Exception as e:
            return {'error': str(e)}
    
    def is_supported_format(self, filepath: str) -> bool:
        """Check if file format is supported"""
        ext = os.path.splitext(filepath)[1].lower()
        return ext in self.supported_formats
    
    def clear_cache(self):
        """Clear all caches"""
        self._file_cache.clear()
        self._process_image.cache_clear()
        self._process_pdf.cache_clear()
        self._process_xml.cache_clear()
        self._process_drawio.cache_clear()
        self._process_vsdx.cache_clear()
        self._process_svg.cache_clear()
        self._process_text.cache_clear()
        self._process_json.cache_clear()
        print("📄 File processor cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'file_cache_size': len(self._file_cache),
            'max_cache_size': self._max_cache_size,
            'lru_cache_stats': {
                'image': self._process_image.cache_info(),
                'pdf': self._process_pdf.cache_info(),
                'xml': self._process_xml.cache_info(),
                'drawio': self._process_drawio.cache_info(),
                'vsdx': self._process_vsdx.cache_info(),
                'svg': self._process_svg.cache_info(),
                'text': self._process_text.cache_info(),
                'json': self._process_json.cache_info()
            }
        }
    
    def _process_image(self, filepath: str) -> Dict[str, Any]:
        """Process image files (PNG, JPG, JPEG)"""
        try:
            with Image.open(filepath) as img:
                # Extract image metadata
                metadata = {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode
                }
                
                # Try to extract EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    metadata['exif'] = dict(img._getexif())
                
                return {
                    'type': 'image',
                    'text': f'Image file: {img.format} format, {img.width}x{img.height} pixels',
                    'metadata': metadata,
                    'image_path': filepath
                }
        except Exception as e:
            return {
                'type': 'image',
                'text': f'Error processing image: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    def _process_pdf(self, filepath: str) -> Dict[str, Any]:
        """Process PDF files"""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                text_content = []
                for page_num, page in enumerate(pdf_reader.pages):
                    text_content.append(f"Page {page_num + 1}: {page.extract_text()}")
                
                metadata = {
                    'num_pages': len(pdf_reader.pages),
                    'title': pdf_reader.metadata.get('/Title', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    'author': pdf_reader.metadata.get('/Author', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    'creator': pdf_reader.metadata.get('/Creator', 'Unknown') if pdf_reader.metadata else 'Unknown'
                }
                
                return {
                    'type': 'pdf',
                    'text': '\n'.join(text_content),
                    'metadata': metadata
                }
        except Exception as e:
            return {
                'type': 'pdf',
                'text': f'Error processing PDF: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    def _process_xml(self, filepath: str) -> Dict[str, Any]:
        """Process XML files"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parse XML
            root = ET.fromstring(content)
            
            # Extract text content and structure
            text_content = self._extract_xml_text(root)
            
            metadata = {
                'root_tag': root.tag,
                'namespace': root.tag.split('}')[0][1:] if '}' in root.tag else None,
                'element_count': len(list(root.iter()))
            }
            
            return {
                'type': 'xml',
                'text': text_content,
                'metadata': metadata,
                'xml_content': content
            }
        except Exception as e:
            return {
                'type': 'xml',
                'text': f'Error processing XML: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    def _process_drawio(self, filepath: str) -> Dict[str, Any]:
        """Process Draw.io files"""
        try:
            # Draw.io files are compressed XML
            with zipfile.ZipFile(filepath, 'r') as zip_file:
                # Look for diagram files
                diagram_files = [f for f in zip_file.namelist() if f.endswith('.xml')]
                
                if not diagram_files:
                    # If no XML files, try to read as uncompressed XML
                    return self._process_xml(filepath)
                
                # Extract and process the main diagram
                main_diagram = diagram_files[0]
                with zip_file.open(main_diagram) as xml_file:
                    xml_content = xml_file.read().decode('utf-8')
                
                # Parse the XML content
                root = ET.fromstring(xml_content)
                text_content = self._extract_drawio_content(root)
                
                metadata = {
                    'diagram_files': diagram_files,
                    'main_diagram': main_diagram,
                    'is_compressed': True
                }
                
                return {
                    'type': 'drawio',
                    'text': text_content,
                    'metadata': metadata,
                    'xml_content': xml_content
                }
        except zipfile.BadZipFile:
            # Try processing as regular XML
            return self._process_xml(filepath)
        except Exception as e:
            return {
                'type': 'drawio',
                'text': f'Error processing Draw.io file: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    def _process_vsdx(self, filepath: str) -> Dict[str, Any]:
        """Process Visio files"""
        try:
            with zipfile.ZipFile(filepath, 'r') as zip_file:
                # Look for content files
                content_files = [f for f in zip_file.namelist() if 'content' in f.lower()]
                
                extracted_content = []
                for content_file in content_files:
                    try:
                        with zip_file.open(content_file) as cf:
                            content = cf.read().decode('utf-8')
                            extracted_content.append(content)
                    except:
                        continue
                
                metadata = {
                    'content_files': content_files,
                    'file_count': len(zip_file.namelist())
                }
                
                return {
                    'type': 'vsdx',
                    'text': '\n'.join(extracted_content),
                    'metadata': metadata
                }
        except Exception as e:
            return {
                'type': 'vsdx',
                'text': f'Error processing VSDX file: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    def _process_svg(self, filepath: str) -> Dict[str, Any]:
        """Process SVG files"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parse SVG
            root = ET.fromstring(content)
            
            # Extract text content
            text_content = self._extract_svg_text(root)
            
            # Extract SVG metadata
            metadata = {
                'width': root.get('width', 'Unknown'),
                'height': root.get('height', 'Unknown'),
                'viewBox': root.get('viewBox', 'Unknown'),
                'element_count': len(list(root.iter()))
            }
            
            return {
                'type': 'svg',
                'text': text_content,
                'metadata': metadata,
                'svg_content': content
            }
        except Exception as e:
            return {
                'type': 'svg',
                'text': f'Error processing SVG: {str(e)}',
                'metadata': {},
                'error': str(e)
            }
    
    def _extract_xml_text(self, element) -> str:
        """Extract text content from XML element"""
        text_parts = []
        
        # Add element tag and attributes
        if element.tag:
            text_parts.append(f"Element: {element.tag}")
        
        if element.attrib:
            text_parts.append(f"Attributes: {element.attrib}")
        
        # Add text content
        if element.text and element.text.strip():
            text_parts.append(f"Text: {element.text.strip()}")
        
        # Recursively process children
        for child in element:
            text_parts.append(self._extract_xml_text(child))
        
        return '\n'.join(text_parts)
    
    def _extract_drawio_content(self, root) -> str:
        """Extract content from Draw.io XML"""
        text_parts = []
        
        # Look for mxCell elements which contain the diagram content
        for cell in root.iter():
            if 'mxCell' in cell.tag:
                # Extract cell attributes
                if cell.attrib:
                    text_parts.append(f"Cell: {cell.attrib}")
            
            # Extract text content
            if cell.text and cell.text.strip():
                text_parts.append(f"Text: {cell.text.strip()}")
        
        return '\n'.join(text_parts)
    
    def _extract_svg_text(self, element) -> str:
        """Extract text content from SVG element"""
        text_parts = []
        
        # Look for text elements
        for text_elem in element.iter():
            if text_elem.tag.endswith('text') or text_elem.tag.endswith('title'):
                if text_elem.text and text_elem.text.strip():
                    text_parts.append(text_elem.text.strip())
        
        return '\n'.join(text_parts)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
