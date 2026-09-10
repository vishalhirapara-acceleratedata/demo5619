"""
Salesforce API Implementation Examples
=====================================

This file contains comprehensive code examples for both Bulk API 2.0 and REST API
implementations, including authentication, error handling, and optimization strategies.
"""

import asyncio
import csv
import json
import time
import requests
import jwt
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SalesforceAuthenticator:
    """
    Handles various Salesforce authentication methods
    """
    
    def __init__(self, client_id: str, client_secret: str, 
                 username: str = None, password: str = None,
                 private_key: str = None, sandbox: bool = False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.private_key = private_key
        self.base_url = "https://test.salesforce.com" if sandbox else "https://login.salesforce.com"
        
    def username_password_auth(self) -> Dict[str, str]:
        """
        OAuth Username-Password Flow
        """
        url = f"{self.base_url}/services/oauth2/token"
        data = {
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': self.username,
            'password': self.password
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        return response.json()
    
    def jwt_bearer_auth(self) -> Dict[str, str]:
        """
        OAuth JWT Bearer Token Flow (Most Secure)
        """
        # Create JWT
        payload = {
            'iss': self.client_id,
            'sub': self.username,
            'aud': self.base_url,
            'exp': datetime.utcnow() + timedelta(minutes=3)
        }
        
        token = jwt.encode(payload, self.private_key, algorithm='RS256')
        
        # Exchange for access token
        url = f"{self.base_url}/services/oauth2/token"
        data = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': token
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        return response.json()
    
    def client_credentials_auth(self) -> Dict[str, str]:
        """
        OAuth Client Credentials Flow (Server-to-Server)
        """
        url = f"{self.base_url}/services/oauth2/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        return response.json()


class SalesforceRESTClient:
    """
    Salesforce REST API Client with comprehensive functionality
    """
    
    def __init__(self, access_token: str, instance_url: str):
        self.access_token = access_token
        self.instance_url = instance_url
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """
        Create HTTP session with retry strategy
        """
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        
        session = requests.Session()
        
        # Retry strategy for transient errors
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            method_whitelist=["HEAD", "GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        return session
    
    def create_record(self, sobject_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a single record
        """
        url = f"{self.instance_url}/services/data/v61.0/sobjects/{sobject_type}/"
        response = self.session.post(url, json=data)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Error creating record: {response.text}")
    
    def update_record(self, sobject_type: str, record_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a single record
        """
        url = f"{self.instance_url}/services/data/v61.0/sobjects/{sobject_type}/{record_id}"
        response = self.session.patch(url, json=data)
        
        if response.status_code == 204:
            return True
        else:
            raise Exception(f"Error updating record: {response.text}")
    
    def delete_record(self, sobject_type: str, record_id: str) -> bool:
        """
        Delete a single record
        """
        url = f"{self.instance_url}/services/data/v61.0/sobjects/{sobject_type}/{record_id}"
        response = self.session.delete(url)
        
        if response.status_code == 204:
            return True
        else:
            raise Exception(f"Error deleting record: {response.text}")
    
    def get_record(self, sobject_type: str, record_id: str, fields: List[str] = None) -> Dict[str, Any]:
        """
        Retrieve a single record
        """
        url = f"{self.instance_url}/services/data/v61.0/sobjects/{sobject_type}/{record_id}"
        
        if fields:
            url += f"?fields={','.join(fields)}"
            
        response = self.session.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error retrieving record: {response.text}")
    
    def sobject_collections_create(self, sobject_type: str, records: List[Dict[str, Any]], 
                                   all_or_none: bool = False) -> Dict[str, Any]:
        """
        Create multiple records using SObject Collections (up to 200 records)
        """
        if len(records) > 200:
            raise ValueError("SObject Collections limited to 200 records per request")
        
        # Prepare records with type information
        formatted_records = []
        for record in records:
            formatted_record = {
                "attributes": {"type": sobject_type},
                **record
            }
            formatted_records.append(formatted_record)
        
        url = f"{self.instance_url}/services/data/v61.0/composite/sobjects"
        data = {
            "allOrNone": all_or_none,
            "records": formatted_records
        }
        
        response = self.session.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error in SObject Collections: {response.text}")
    
    def composite_request(self, requests_data: List[Dict[str, Any]], 
                          all_or_none: bool = True) -> Dict[str, Any]:
        """
        Execute multiple operations in a single call (up to 25 subrequests)
        """
        if len(requests_data) > 25:
            raise ValueError("Composite API limited to 25 subrequests")
        
        url = f"{self.instance_url}/services/data/v61.0/composite"
        data = {
            "allOrNone": all_or_none,
            "compositeRequest": requests_data
        }
        
        response = self.session.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error in Composite request: {response.text}")
    
    def query(self, soql: str) -> Dict[str, Any]:
        """
        Execute SOQL query
        """
        url = f"{self.instance_url}/services/data/v61.0/query/"
        params = {'q': soql}
        
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error in query: {response.text}")
    
    def query_all(self, soql: str) -> List[Dict[str, Any]]:
        """
        Execute SOQL query and return all records (handles pagination)
        """
        all_records = []
        response = self.query(soql)
        
        all_records.extend(response['records'])
        
        # Handle pagination
        while not response['done']:
            next_url = response['nextRecordsUrl']
            response = self.session.get(f"{self.instance_url}{next_url}").json()
            all_records.extend(response['records'])
        
        return all_records


class SalesforceBulkClient:
    """
    Salesforce Bulk API 2.0 Client
    """
    
    def __init__(self, access_token: str, instance_url: str):
        self.access_token = access_token
        self.instance_url = instance_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })
    
    def create_job(self, sobject_type: str, operation: str, 
                   external_id_field: str = None, line_ending: str = 'LF') -> Dict[str, Any]:
        """
        Create a new bulk job
        
        Args:
            sobject_type: Type of Salesforce object (e.g., 'Account', 'Contact')
            operation: 'insert', 'update', 'upsert', 'delete', or 'query'
            external_id_field: Required for upsert operations
            line_ending: 'LF' (Linux/Mac) or 'CRLF' (Windows)
        """
        url = f"{self.instance_url}/services/data/v61.0/jobs/ingest"
        
        job_data = {
            "object": sobject_type,
            "operation": operation,
            "lineEnding": line_ending
        }
        
        if operation == 'upsert' and external_id_field:
            job_data["externalIdFieldName"] = external_id_field
        
        response = self.session.post(url, json=job_data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error creating bulk job: {response.text}")
    
    def upload_job_data(self, job_id: str, data: str, content_type: str = 'text/csv') -> bool:
        """
        Upload data to bulk job
        
        Args:
            job_id: ID of the bulk job
            data: CSV or JSON data as string
            content_type: 'text/csv' or 'application/json'
        """
        url = f"{self.instance_url}/services/data/v61.0/jobs/ingest/{job_id}/batches"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': content_type,
            'Accept': 'application/json'
        }
        
        response = requests.put(url, data=data.encode('utf-8'), headers=headers)
        
        if response.status_code == 201:
            return True
        else:
            raise Exception(f"Error uploading data: {response.text}")
    
    def close_job(self, job_id: str) -> Dict[str, Any]:
        """
        Close a bulk job to start processing
        """
        url = f"{self.instance_url}/services/data/v61.0/jobs/ingest/{job_id}"
        data = {"state": "UploadComplete"}
        
        response = self.session.patch(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error closing job: {response.text}")
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get job status and statistics
        """
        url = f"{self.instance_url}/services/data/v61.0/jobs/ingest/{job_id}"
        response = self.session.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error getting job status: {response.text}")
    
    def wait_for_job_completion(self, job_id: str, max_wait_time: int = 3600, 
                                poll_interval: int = 30) -> Dict[str, Any]:
        """
        Wait for job to complete with exponential backoff
        """
        start_time = time.time()
        wait_time = poll_interval
        max_wait = 300  # Maximum 5 minutes between polls
        
        while time.time() - start_time < max_wait_time:
            job_status = self.get_job_status(job_id)
            state = job_status['state']
            
            logger.info(f"Job {job_id} state: {state}")
            
            if state in ['JobComplete', 'Failed', 'Aborted']:
                return job_status
            
            # Exponential backoff
            time.sleep(wait_time)
            wait_time = min(wait_time * 1.5, max_wait)
        
        raise TimeoutError(f"Job {job_id} did not complete within {max_wait_time} seconds")
    
    def get_job_results(self, job_id: str, result_type: str = 'successful') -> str:
        """
        Get job results
        
        Args:
            job_id: ID of the bulk job
            result_type: 'successful', 'failed', or 'unprocessed'
        """
        url = f"{self.instance_url}/services/data/v61.0/jobs/ingest/{job_id}/{result_type}Results/"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'text/csv'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Error getting job results: {response.text}")
    
    def bulk_insert(self, sobject_type: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        High-level method for bulk insert operation
        """
        # Create job
        job = self.create_job(sobject_type, 'insert')
        job_id = job['id']
        
        try:
            # Convert records to CSV
            csv_data = self._convert_to_csv(records)
            
            # Upload data
            self.upload_job_data(job_id, csv_data)
            
            # Close job and wait for completion
            self.close_job(job_id)
            result = self.wait_for_job_completion(job_id)
            
            return result
            
        except Exception as e:
            # Abort job on error
            self._abort_job(job_id)
            raise e
    
    def bulk_upsert(self, sobject_type: str, records: List[Dict[str, Any]], 
                    external_id_field: str) -> Dict[str, Any]:
        """
        High-level method for bulk upsert operation
        """
        # Create job
        job = self.create_job(sobject_type, 'upsert', external_id_field)
        job_id = job['id']
        
        try:
            # Convert records to CSV
            csv_data = self._convert_to_csv(records)
            
            # Upload data
            self.upload_job_data(job_id, csv_data)
            
            # Close job and wait for completion
            self.close_job(job_id)
            result = self.wait_for_job_completion(job_id)
            
            return result
            
        except Exception as e:
            # Abort job on error
            self._abort_job(job_id)
            raise e
    
    def _convert_to_csv(self, records: List[Dict[str, Any]]) -> str:
        """
        Convert list of dictionaries to CSV string
        """
        if not records:
            return ""
        
        output = io.StringIO()
        fieldnames = records[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        for record in records:
            writer.writerow(record)
        
        return output.getvalue()
    
    def _abort_job(self, job_id: str) -> None:
        """
        Abort a bulk job
        """
        try:
            url = f"{self.instance_url}/services/data/v61.0/jobs/ingest/{job_id}"
            data = {"state": "Aborted"}
            self.session.patch(url, json=data)
        except Exception as e:
            logger.warning(f"Failed to abort job {job_id}: {e}")


class SalesforceDataManager:
    """
    High-level data manager that intelligently chooses between REST and Bulk APIs
    """
    
    def __init__(self, access_token: str, instance_url: str):
        self.rest_client = SalesforceRESTClient(access_token, instance_url)
        self.bulk_client = SalesforceBulkClient(access_token, instance_url)
    
    def upsert_records(self, sobject_type: str, records: List[Dict[str, Any]], 
                       external_id_field: str = None) -> Dict[str, Any]:
        """
        Intelligently route upsert operations based on volume
        """
        record_count = len(records)
        
        if record_count > 2000:
            logger.info(f"Using Bulk API for {record_count} records")
            if not external_id_field:
                raise ValueError("external_id_field required for bulk upsert")
            return self.bulk_client.bulk_upsert(sobject_type, records, external_id_field)
        
        elif record_count > 200:
            logger.info(f"Using REST API SObject Collections for {record_count} records")
            return self._rest_batch_upsert(sobject_type, records, external_id_field)
        
        else:
            logger.info(f"Using REST API individual operations for {record_count} records")
            return self._rest_individual_upsert(sobject_type, records)
    
    def _rest_batch_upsert(self, sobject_type: str, records: List[Dict[str, Any]], 
                           external_id_field: str) -> Dict[str, Any]:
        """
        Handle medium-volume upserts using SObject Collections
        """
        results = []
        batch_size = 200
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            # For upsert, we need to use Composite API with individual PATCH requests
            # SObject Collections doesn't support upsert directly
            composite_requests = []
            
            for j, record in enumerate(batch):
                if external_id_field and external_id_field in record:
                    external_id = record[external_id_field]
                    # Remove the external ID from the record data
                    record_data = {k: v for k, v in record.items() if k != external_id_field}
                    
                    composite_requests.append({
                        "method": "PATCH",
                        "url": f"/services/data/v61.0/sobjects/{sobject_type}/{external_id_field}/{external_id}",
                        "referenceId": f"ref{j}",
                        "body": record_data
                    })
            
            if composite_requests:
                batch_result = self.rest_client.composite_request(composite_requests, all_or_none=False)
                results.append(batch_result)
        
        return {"batch_results": results}
    
    def _rest_individual_upsert(self, sobject_type: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle small-volume operations using individual REST calls
        """
        results = {"successful": [], "failed": []}
        
        for record in records:
            try:
                result = self.rest_client.create_record(sobject_type, record)
                results["successful"].append(result)
            except Exception as e:
                results["failed"].append({"record": record, "error": str(e)})
        
        return results


# Usage Examples
def example_rest_api_usage():
    """
    Example of REST API usage patterns
    """
    # Initialize authenticator
    auth = SalesforceAuthenticator(
        client_id="your_client_id",
        client_secret="your_client_secret",
        username="your_username",
        password="your_password_and_token"
    )
    
    # Authenticate
    auth_response = auth.username_password_auth()
    access_token = auth_response['access_token']
    instance_url = auth_response['instance_url']
    
    # Initialize REST client
    sf = SalesforceRESTClient(access_token, instance_url)
    
    # Example 1: Create a single record
    account_data = {
        "Name": "Example Corporation",
        "Type": "Customer",
        "Industry": "Technology"
    }
    account = sf.create_record("Account", account_data)
    print(f"Created account: {account['id']}")
    
    # Example 2: Bulk create using SObject Collections
    contacts = []
    for i in range(50):
        contacts.append({
            "FirstName": f"Contact{i}",
            "LastName": f"Test{i}",
            "Email": f"contact{i}@example.com",
            "AccountId": account['id']
        })
    
    result = sf.sobject_collections_create("Contact", contacts)
    print(f"Created {len(result)} contacts")
    
    # Example 3: Composite request for related records
    composite_requests = [
        {
            "method": "POST",
            "url": "/services/data/v61.0/sobjects/Account",
            "referenceId": "NewAccount",
            "body": {
                "Name": "Composite Test Account",
                "Type": "Prospect"
            }
        },
        {
            "method": "POST",
            "url": "/services/data/v61.0/sobjects/Contact",
            "referenceId": "NewContact",
            "body": {
                "FirstName": "John",
                "LastName": "Doe",
                "AccountId": "@{NewAccount.id}"
            }
        }
    ]
    
    composite_result = sf.composite_request(composite_requests)
    print("Composite request completed")


def example_bulk_api_usage():
    """
    Example of Bulk API usage patterns
    """
    # Initialize authenticator
    auth = SalesforceAuthenticator(
        client_id="your_client_id",
        client_secret="your_client_secret",
        username="your_username",
        password="your_password_and_token"
    )
    
    # Authenticate
    auth_response = auth.username_password_auth()
    access_token = auth_response['access_token']
    instance_url = auth_response['instance_url']
    
    # Initialize Bulk client
    bulk = SalesforceBulkClient(access_token, instance_url)
    
    # Example 1: Bulk insert
    accounts = []
    for i in range(10000):
        accounts.append({
            "Name": f"Bulk Account {i}",
            "Type": "Customer",
            "Industry": "Technology"
        })
    
    result = bulk.bulk_insert("Account", accounts)
    print(f"Bulk insert completed: {result['numberRecordsProcessed']} records processed")
    
    # Example 2: Bulk upsert with external ID
    products = []
    for i in range(5000):
        products.append({
            "Name": f"Product {i}",
            "ProductCode": f"PROD-{i:05d}",
            "External_ID__c": f"EXT-{i:05d}",
            "IsActive": True
        })
    
    upsert_result = bulk.bulk_upsert("Product2", products, "External_ID__c")
    print(f"Bulk upsert completed: {upsert_result['numberRecordsProcessed']} records processed")


def example_hybrid_usage():
    """
    Example of intelligent API selection
    """
    # Initialize authenticator
    auth = SalesforceAuthenticator(
        client_id="your_client_id",
        client_secret="your_client_secret",
        username="your_username",
        password="your_password_and_token"
    )
    
    # Authenticate
    auth_response = auth.username_password_auth()
    access_token = auth_response['access_token']
    instance_url = auth_response['instance_url']
    
    # Initialize data manager
    dm = SalesforceDataManager(access_token, instance_url)
    
    # Small batch - uses REST API
    small_batch = [{"Name": f"Account {i}"} for i in range(50)]
    result1 = dm.upsert_records("Account", small_batch)
    
    # Medium batch - uses SObject Collections
    medium_batch = [{"Name": f"Account {i}"} for i in range(500)]
    result2 = dm.upsert_records("Account", medium_batch)
    
    # Large batch - uses Bulk API
    large_batch = [{"Name": f"Account {i}", "External_ID__c": f"EXT-{i}"} for i in range(5000)]
    result3 = dm.upsert_records("Account", large_batch, external_id_field="External_ID__c")
    
    print("Hybrid approach completed successfully")


if __name__ == "__main__":
    # Run examples (uncomment as needed)
    # example_rest_api_usage()
    # example_bulk_api_usage()
    # example_hybrid_usage()
    
    print("Salesforce API examples loaded successfully")
    print("Uncomment the example functions to run demonstrations")