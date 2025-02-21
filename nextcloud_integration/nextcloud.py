import requests
import frappe
import os
import time
import xml.etree.ElementTree as ET

# Nextcloud credentials
nextcloud_config = frappe.get_site_config().get('nextcloud_credentials', {})

NEXTCLOUD_URL = nextcloud_config.get('NEXTCLOUD_URL')
NEXTCLOUD_SHARING_API = nextcloud_config.get('NEXTCLOUD_SHARING_API')
USERNAME = nextcloud_config.get('USERNAME')
PASSWORD = nextcloud_config.get('PASSWORD')



def upload_to_nextcloud(file_path, file_name, folder):

    try:
        upload_url = f"{NEXTCLOUD_URL}/{folder}/{file_name}"

        # Check if the file exists in Nextcloud
        response = requests.head(upload_url, auth=(USERNAME, PASSWORD))

        # If the file exists, modify the filename to avoid overwriting
        if response.status_code == 200:
            print(f"File '{file_name}' already exists in Nextcloud. Renaming the file.")
            name, ext = os.path.splitext(file_name)
            timestamp = int(time.time())
            file_name = f"{name}_{timestamp}{ext}"
            upload_url = f"{NEXTCLOUD_URL}/{folder}/{file_name}"
        

        # Upload the file
        with open(file_path, "rb") as file_data:
            response = requests.put(
                upload_url,
                data=file_data,
                auth=(USERNAME, PASSWORD)
            )

        if response.status_code == 201:
            print('File uploaded successfully!')
            return {"status": "success", "nextcloud_url": upload_url, "message": "File uploaded successfully!"}
        else:
            return {"status": "error", "code": response.status_code, "message": response.text}

    except Exception as e:
        return {"status": "error", "message": str(e)}



def create_folder_if_not_exists(folder_path):
    try:
        folder_parts = folder_path.split('/')
        current_path = NEXTCLOUD_URL

        for part in folder_parts:
            current_path = f"{current_path}/{part}"
            
            # Check if the folder exists
            response = requests.request("PROPFIND", current_path, auth=(USERNAME, PASSWORD))

            if response.status_code == 404:  # Folder does not exist, create it
                create_response = requests.request("MKCOL", current_path, auth=(USERNAME, PASSWORD))

                if create_response.status_code not in [201, 405]:  # 201: Created, 405: Already exists
                    frappe.logger().error(f"Failed to create folder: {current_path}, Status Code: {create_response.status_code}, Response: {create_response.text}")
                    frappe.throw(f"Failed to create folder {current_path}")

            elif response.status_code not in [207, 200]:  # 207: Multi-status (exists), 200: OK
                frappe.logger().error(f"Error checking folder existence: {current_path}, Status Code: {response.status_code}")
                frappe.throw(f"Error checking folder existence: {current_path}")

        frappe.logger().info(f"Folder structure {folder_path} ensured in Nextcloud.")

    except Exception as e:
        frappe.logger().error(f"Error creating folders: {str(e)}")
        frappe.throw(f"Error creating folders: {str(e)}")


def create_shareable_link(file_path, file_name, folder):

    try:
      
        nextcloud_file_path = f"/{folder}/{file_name}"

        headers = {"OCS-APIRequest": "true"}
        response = requests.post(
            NEXTCLOUD_SHARING_API,
            headers=headers,
            auth=(USERNAME, PASSWORD),
            data={
                "path": nextcloud_file_path,
                "shareType": 3,  # Public link
                "permissions": 1,  # Read-only permission
            }
        )

        if response.status_code == 200:
            root = ET.fromstring(response.text)

            share_link = root.find(".//url")  

            if share_link is not None:
                print(share_link.text)
                return {"status": "success", "shareable_link": share_link.text, "message": "Shareable link created successfully!"}
            else:
                return {"status": "error", "message": "Share link not found in response."}
        else:
            print('error')
            return {"status": "error", "code": response.status_code, "message": response.text}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_nextcloud_file(self, method=None):

    if not NEXTCLOUD_URL or not PASSWORD:
        msg = "Nextcloud credentials are missing in site_config.json"
        frappe.logger().error(msg)
        return

    file_name = self.custom_nextcloud_filename
    if not file_name:
        msg = "Error: No Nextcloud file name provided."
        frappe.logger().error(msg)
        return

    if self.attached_to_doctype and self.attached_to_name:
        folder_name = f"{self.attached_to_doctype}/{self.attached_to_name}"
    else:
        folder_name = "File Uploads"

    file_path = f"{folder_name}/{file_name}"  
    file_url = f"{NEXTCLOUD_URL}/{file_path}"  

    msg = f"Attempting to delete file from: {file_url}"
    frappe.logger().info(msg)

    try:
        response = requests.delete(file_url, auth=(USERNAME, PASSWORD))

        if response.status_code == 204:
            msg = f"Successfully deleted: {file_path}"
            frappe.logger().info(msg)
        elif response.status_code == 404:
            msg = f"File not found: {file_path}"
            frappe.logger().warning(msg)
        else:
            msg = f"Failed to delete {file_path}: {response.text}"
            frappe.logger().error(msg)

    except Exception as e:
        msg = f"Exception while deleting Nextcloud file: {str(e)}"
        frappe.logger().error(msg)


def delete_nextcloud_folder(self, method=None):
    if not NEXTCLOUD_URL or not PASSWORD:
        msg = "Nextcloud credentials are missing in site_config.json"
        frappe.logger().error(msg)
        return

    folder_path = f"{self.doctype}/{self.name}"
    folder_url = f"{NEXTCLOUD_URL}/{folder_path}"  

    msg = f"Attempting to delete folder: {folder_url}"
    frappe.logger().info(msg)

    try:
        response = requests.delete(folder_url, auth=(USERNAME, PASSWORD))

        if response.status_code == 204:
            msg = f"Successfully deleted folder: {folder_path}"
            frappe.logger().info(msg)
        elif response.status_code == 404:
            msg = f"Folder not found: {folder_path}"
            frappe.logger().warning(msg)
        else:
            msg = f"Failed to delete folder {folder_path}: {response.text}"
            frappe.logger().error(msg)

    except Exception as e:
        msg = f"Exception while deleting Nextcloud folder: {str(e)}"
        frappe.logger().error(msg)
