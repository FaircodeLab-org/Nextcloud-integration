import frappe
from nextcloud_integration.nextcloud import upload_to_nextcloud, create_shareable_link, create_folder_if_not_exists
import os

def upload_attachments(doc, method):
    if doc.attached_to_doctype and doc.attached_to_name:
        print(doc.attached_to_doctype)
        print(doc.attached_to_name)
    if doc.file_name:
        print(doc.file_name)
        try:
            # Determine file path based on whether the file is private or public
            if doc.is_private:
                file_path = frappe.get_site_path("private", "files", doc.file_name)
            else:
                file_path = frappe.get_site_path("public", "files", doc.file_name)

            frappe.logger().info(f"File path: {file_path}")
            # Determine the Nextcloud folder
            print(file_path)
            if doc.attached_to_doctype and doc.attached_to_name:
                print('yes')
                folder = f"{doc.attached_to_doctype}/{doc.attached_to_name}"
                print(folder)
            else:
                print('normal')
                folder = "File Uploads"  # Default folder for unattached files

            # Ensure the folder exists in Nextcloud
            create_folder_if_not_exists(folder)
            # Upload the file to Nextcloud
            result = upload_to_nextcloud(file_path, doc.file_name, folder)
            print(result)
            frappe.logger().info(f"Upload result: {result}")

            # Extract Nextcloud file path
            nextcloud_url = result.get("nextcloud_url")
            if not nextcloud_url:
                frappe.throw("Nextcloud URL not returned after upload.")

            file_name = nextcloud_url.split('/')[-1]
            frappe.logger().info(f"Nextcloud file path: {nextcloud_url}, File name: {file_name}")

            # Generate a public share link
            share_result = create_shareable_link(nextcloud_url, file_name, folder)
            frappe.logger().info(f"Share result: {share_result}")

            # Check if share_result contains the expected data
            if not share_result.get('shareable_link'):
                frappe.throw("Public URL not generated from Nextcloud.")

            public_url = share_result['shareable_link']
            frappe.logger().info(f"Generated public URL: {public_url}")

            # Update custom fields and file_url
            doc.custom_nextcloud_url = public_url
            doc.custom_nextcloud_filename = file_name
            doc.file_url = public_url  # Update the standard file_url field to point to the Nextcloud link
            frappe.logger().info(f"Before saving: {doc.custom_nextcloud_url}, {doc.custom_nextcloud_filename}, {doc.file_url}")

            # Save the document
            doc.save()
            frappe.logger().info("Document saved successfully.")

            # Confirm saved values
            saved_doc = frappe.get_doc("File", doc.name)
            frappe.logger().info(f"Saved custom_nextcloud_url: {saved_doc.custom_nextcloud_url}, Saved file_url: {saved_doc.file_url}")

            # Delete the local file after successful upload
            if os.path.exists(file_path):
                os.remove(file_path)
                frappe.logger().info(f"Local file deleted: {file_path}")
            else:
                frappe.logger().warning(f"Local file not found for deletion: {file_path}")

        except Exception as e:
            frappe.logger().error(f"An error occurred: {str(e)}")
            # Ensure public_url and file_name are set in case of error
            public_url = public_url if 'public_url' in locals() else None
            file_name = file_name if 'file_name' in locals() else None
            
            # Fallback to update the database directly if there's an error
            frappe.db.set_value("File", doc.name, {
                "custom_nextcloud_url": public_url if public_url else 'default',
                "custom_nextcloud_filename": file_name,
                "file_url": public_url if public_url else doc.file_url  # Fallback to leave file_url unchanged
            })
            frappe.db.commit()
            frappe.logger().info("Fields updated directly in the database as a fallback.")
