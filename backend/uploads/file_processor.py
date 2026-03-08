import pandas as pd
import csv
from typing import Dict, List, Any, Tuple
from django.core.files.uploadedfile import UploadedFile


class FileProcessor:
    """Utility class for processing CSV and Excel files"""
    
    @staticmethod
    def read_file(file: UploadedFile) -> Tuple[pd.DataFrame, str]:
        """
        Read CSV or Excel file and return DataFrame
        
        Returns:
            Tuple of (DataFrame, error_message)
        """
        try:
            file_ext = file.name.split('.')[-1].lower()
            
            if file_ext == 'csv':
                # Try different encodings
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                    try:
                        file.seek(0)
                        df = pd.read_csv(file, encoding=encoding)
                        return df, None
                    except UnicodeDecodeError:
                        continue
                return None, "Unable to decode CSV file. Please check file encoding."
            
            elif file_ext in ['xlsx', 'xls']:
                file.seek(0)
                df = pd.read_excel(file, engine='openpyxl' if file_ext == 'xlsx' else None)
                return df, None
            
            else:
                return None, f"Unsupported file format: {file_ext}"
        
        except Exception as e:
            return None, f"Error reading file: {str(e)}"
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate DataFrame structure and content
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append("File is empty or contains no data")
            return False, errors
        
        # Check for minimum columns
        if len(df.columns) == 0:
            errors.append("File must contain at least one column")
            return False, errors
        
        # Check for duplicate column names
        if df.columns.duplicated().any():
            duplicates = df.columns[df.columns.duplicated()].tolist()
            errors.append(f"Duplicate column names found: {', '.join(duplicates)}")
        
        # Check for completely empty columns
        empty_cols = df.columns[df.isnull().all()].tolist()
        if empty_cols:
            errors.append(f"Empty columns found: {', '.join(empty_cols)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def get_preview_data(df: pd.DataFrame, max_rows: int = 10) -> List[Dict[str, Any]]:
        """
        Get preview of data (first N rows)
        
        Returns:
            List of dictionaries representing rows
        """
        preview_df = df.head(max_rows)
        
        # Replace NaN with None for JSON serialization
        preview_df = preview_df.where(pd.notnull(preview_df), None)
        
        return preview_df.to_dict('records')
    
    @staticmethod
    def get_column_info(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Get information about columns
        
        Returns:
            List of column metadata
        """
        column_info = []
        
        for col in df.columns:
            info = {
                'name': col,
                'type': str(df[col].dtype),
                'non_null_count': int(df[col].count()),
                'null_count': int(df[col].isnull().sum()),
                'unique_count': int(df[col].nunique()),
            }
            
            # Get sample values (first 5 non-null)
            sample_values = df[col].dropna().head(5).tolist()
            info['sample_values'] = [str(v) for v in sample_values]
            
            column_info.append(info)
        
        return column_info
    
    @staticmethod
    def validate_row(row_data: Dict[str, Any], rules: Dict[str, Any] = None) -> Tuple[bool, List[str]]:
        """
        Validate individual row data
        
        Args:
            row_data: Dictionary of row data
            rules: Optional validation rules
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Basic validation - check for required fields
        if rules and 'required_fields' in rules:
            for field in rules['required_fields']:
                if field not in row_data or row_data[field] is None or row_data[field] == '':
                    errors.append(f"Required field '{field}' is missing or empty")
        
        # Type validation
        if rules and 'field_types' in rules:
            for field, expected_type in rules['field_types'].items():
                if field in row_data and row_data[field] is not None:
                    try:
                        if expected_type == 'int':
                            int(row_data[field])
                        elif expected_type == 'float':
                            float(row_data[field])
                        elif expected_type == 'email':
                            if '@' not in str(row_data[field]):
                                errors.append(f"Invalid email format in field '{field}'")
                    except (ValueError, TypeError):
                        errors.append(f"Invalid {expected_type} value in field '{field}'")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def process_dataframe(df: pd.DataFrame, validation_rules: Dict[str, Any] = None) -> Tuple[List[Dict], List[Dict]]:
        """
        Process DataFrame and return valid and invalid records
        
        Returns:
            Tuple of (valid_records, invalid_records)
        """
        valid_records = []
        invalid_records = []
        
        for idx, row in df.iterrows():
            # Convert row to dictionary
            row_dict = row.where(pd.notnull(row), None).to_dict()
            
            # Validate row
            is_valid, errors = FileProcessor.validate_row(row_dict, validation_rules)
            
            record = {
                'row_number': int(idx) + 1,  # 1-indexed
                'data': row_dict,
                'is_valid': is_valid,
                'errors': errors
            }
            
            if is_valid:
                valid_records.append(record)
            else:
                invalid_records.append(record)
        
        return valid_records, invalid_records