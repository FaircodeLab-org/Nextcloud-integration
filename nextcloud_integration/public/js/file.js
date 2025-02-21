frappe.ui.form.on("File", {
    refresh: function (frm) {
        if (!frm.doc.is_folder) {
            // Add a custom download button
            frm.add_custom_button(__("Download"), () => {
                frm.trigger("download");
            }, "fa fa-download");
        }

        if (!frm.doc.is_private) {
            frm.dashboard.set_headline(
                __("This file is public. It can be accessed without authentication."),
                "orange"
            );
        }

        frm.toggle_display("preview", false);

        // Preview different file types
        frm.trigger("preview_file");

        let is_raster_image = /\.(gif|jpg|jpeg|tiff|png)$/i.test(frm.doc.file_url);
        let is_optimizable = !frm.doc.is_folder && is_raster_image && frm.doc.file_size > 0;

        // Add optimize button
        is_optimizable && frm.add_custom_button(__("Optimize"), () => frm.trigger("optimize"));

        // Add unzip button
        if (frm.doc.file_name && frm.doc.file_name.split(".").splice(-1)[0] === "zip") {
            frm.add_custom_button(__("Unzip"), () => frm.trigger("unzip"));
        }
    },

    //preview file for old and new files. For nextcloud files, /download will be added for nextcloud share urls to preview the image
    preview_file: function (frm) {
        let $preview = "";
        let file_name = frm.doc.file_name || "";  
        let file_url = frm.doc.file_url || "";   
        let is_image = /\.(gif|jpg|jpeg|tiff|png)$/i.test(file_name); 
    
        // Check if file URL belongs to Nextcloud shared link (contains /s/)
        let is_nextcloud_shared = file_url.includes("/s/");
    
        if (file_url) {
            //checking if it is an image
            if (is_image) {
                // Append "/download" only for Nextcloud shared links
                let preview_url = is_nextcloud_shared ? `${file_url}/download` : file_url;
    
                // Display the image
                $preview = `<div class="custom_image_preview">
                    <img src="${frappe.utils.escape_html(preview_url)}" 
                         alt="Shared Image" 
                         style="max-width: 100%; height: auto;">
                </div>`;
            } else {
                // Display "No preview available" message
                $preview = `<div class="custom_no_preview">
                    <p>No preview available</p>
                    <a href="${frappe.utils.escape_html(file_url)}" 
                       class="btn btn-primary" 
                       target="_blank">
                        ${__("View in Nextcloud")}
                    </a>
                </div>`;
            }
        }
    
        if ($preview) {
            frm.toggle_display("preview", true);
            frm.get_field("preview_html").$wrapper.html($preview);
        }
    },

    download: function (frm) {
        let file_url = frm.doc.custom_nextcloud_url;  
    
        if (file_url) {
            console.log(file_url + '/download');

        }
    },

    optimize: function (frm) {
        frappe.show_alert(__("Optimizing image..."));
        frm.call("optimize_file").then(() => {
            frappe.show_alert(__("Image optimized"));
        });
    },

    unzip: function (frm) {
        frappe.call({
            method: "frappe.core.api.file.unzip_file",
            args: {
                name: frm.doc.name,
            },
            callback: function () {
                frappe.set_route("List", "File");
            },
        });
    },
});
