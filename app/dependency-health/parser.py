"""
Dependency Parser Module
Parses requirements.txt files to extract dependency information
"""
import re
from typing import List, Dict, Optional
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet

class DependencyParser:
    """Parse and extract dependency information from requirements files"""
    
    def __init__(self):
        self.dependencies = []
    
    def parse_requirements_file(self, file_path: str) -> List[Dict[str, str]]:
        """
        Parse a requirements.txt file and extract dependency information
        
        Args:
            file_path (str): Path to the requirements.txt file
            
        Returns:
            List[Dict]: List of dependency dictionaries with name, version, etc.
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Skip git URLs and other special requirements
                if line.startswith(('git+', 'hg+', 'svn+', 'bzr+', '-e')):
                    continue
                
                try:
                    # Parse the requirement using packaging library
                    req = Requirement(line)
                    
                    dependency_info = {
                        'name': req.name,
                        'raw_line': line,
                        'line_number': line_num,
                        'specifier': str(req.specifier) if req.specifier else '',
                        'extras': list(req.extras) if req.extras else [],
                        'marker': str(req.marker) if req.marker else ''
                    }
                    
                    # Extract version information
                    if req.specifier:
                        versions = []
                        for spec in req.specifier:
                            versions.append({
                                'operator': spec.operator,
                                'version': spec.version
                            })
                        dependency_info['versions'] = versions
                    else:
                        dependency_info['versions'] = []
                    
                    dependencies.append(dependency_info)
                    
                except Exception as e:
                    # Handle malformed requirements
                    print(f"Warning: Could not parse line {line_num}: '{line}' - {str(e)}")
                    
        except FileNotFoundError:
            print(f"Error: Requirements file '{file_path}' not found")
            return []
        except Exception as e:
            print(f"Error reading requirements file: {str(e)}")
            return []
            
        self.dependencies = dependencies
        return dependencies
    
    def get_dependency_names(self) -> List[str]:
        """
        Get a list of all dependency names
        
        Returns:
            List[str]: List of dependency names
        """
        return [dep['name'] for dep in self.dependencies]
    
    def get_dependency_by_name(self, name: str) -> Optional[Dict]:
        """
        Get dependency information by name
        
        Args:
            name (str): Name of the dependency
            
        Returns:
            Optional[Dict]: Dependency information or None if not found
        """
        for dep in self.dependencies:
            if dep['name'].lower() == name.lower():
                return dep
        return None
    
    def extract_version_from_spec(self, specifier: str) -> Optional[str]:
        """
        Extract a specific version from version specifier
        
        Args:
            specifier (str): Version specifier string
            
        Returns:
            Optional[str]: Extracted version or None
        """
        if not specifier:
            return None
            
        # Look for exact version (==)
        exact_match = re.search(r'==\s*([^\s,;]+)', specifier)
        if exact_match:
            return exact_match.group(1)
            
        # Look for minimum version (>=)
        min_match = re.search(r'>=\s*([^\s,;]+)', specifier)
        if min_match:
            return min_match.group(1)
            
        # Look for any version number
        version_match = re.search(r'([0-9]+(?:\.[0-9]+)*(?:[a-zA-Z][0-9]*)?)', specifier)
        if version_match:
            return version_match.group(1)
            
        return None