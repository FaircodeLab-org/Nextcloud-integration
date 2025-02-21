# Nextcloud Integration

## Overview

The **Nextcloud Integration** app enables seamless file management between ERPNext and Nextcloud. It automates folder creation, file uploads, deletions, and provides file preview functionality directly in ERPNext.

---

## Features

- ✅ **Automatic Folder Creation** – Organizes files in Nextcloud by DocType and document.  
- 📂 **Structured File Organization** – Ensures each ERPNext document has a corresponding folder in Nextcloud.  
- 📤 **File Uploads** – Attachments in ERPNext are automatically uploaded to Nextcloud.  
- 🗑️ **File and Folder Deletion** – Deleting a file in ERPNext removes it from Nextcloud.  
- 🖼️ **Enhanced File Preview** – Image previews directly in ERPNext; other files have a Nextcloud redirect.  
- 🔗 **Auto-Generated Share Links** – Every uploaded file gets a shareable link stored in ERPNext.  

---

## Installation

To install the **Nextcloud Integration** app, follow these steps:

### **1️⃣ Get the App**
Run the following command in your **bench** directory:

```bash
bench get-app nextcloud_integration https://github.com/FaircodeLab-org/Nextcloud-integration.git
```

### **2️⃣ Install the App**
Install it on your site:

```bash
bench --site your-site-name install-app nextcloud_integration
```

### **3️⃣ Apply Migrations**
Ensure database migrations are applied:

```bash
bench migrate
```

### **4️⃣ Restart Bench**
```bash
bench restart
```

---

## Configuration

### **🔑 Add Nextcloud Credentials**
Before using the app, you need to configure Nextcloud credentials in **site_config.json**.

#### **Steps:**
1. Open `sites/common_site_config.json` or `sites/{your-site-name}/site_config.json`
2. Add the following JSON block:

```json
"nextcloud_credentials": {
    "NEXTCLOUD_URL": "https://website.com/remote.php/dav/files/username",
    "NEXTCLOUD_SHARING_API": "https://website.com/ocs/v2.php/apps/files_sharing/api/v1/shares",
    "USERNAME": "Nextcloud username",
    "PASSWORD": "Nextcloud password"
}
```

3. Save the file and restart bench:

```bash
bench restart
```

---

## Usage

### 📂 **File Upload and Folder Creation**
- When a user **attaches a file** in ERPNext:
  - The system **checks if a folder exists** in Nextcloud.
  - If not, it **creates a folder** based on the ERPNext DocType and document name.
  - The **file is uploaded** to the corresponding folder.
  - A **Nextcloud share link is generated** and stored in ERPNext.

### 🗑️ **File and Folder Deletion**
- If a file is deleted in ERPNext:
  - The file is **removed from Nextcloud**.
  - If the folder is empty, it can also be deleted.

### 🖼️ **File Preview**
- If the file is **an image**, it is displayed directly in ERPNext.
- If the file **cannot be previewed**, a **button redirects** the user to Nextcloud.

### 🔗 **Auto-Generated Share Links**
- Every uploaded file gets a **Nextcloud shareable link**, stored in ERPNext.

---


## Contributing

We welcome contributions! 🚀  
To contribute:

1. **Fork the repository**  
2. **Create a feature branch**  

   ```bash
   git checkout -b feature-new-feature
   ```

3. **Commit your changes**  

   ```bash
   git commit -m "Add new feature"
   ```

4. **Push to your fork**  

   ```bash
   git push origin feature-new-feature
   ```

5. **Submit a pull request**  

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Support

For issues, create a ticket on our [GitHub Issues](https://github.com/FaircodeLab-org/Nextcloud-integration/issues) page.
