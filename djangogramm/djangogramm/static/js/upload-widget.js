function initCloudinaryUploadWidget(cloudName, uploadPreset) {
    const hiddenFieldId = "image_urls"; // Hidden field ID
    const buttonId = "upload_widget";  // Button ID
    const thumbnailsContainerId = "thumbnails"; // Thumbnails container ID
    var uploadWidget = cloudinary.createUploadWidget({
        cloudName: cloudName,
        uploadPreset: uploadPreset,
        showPoweredBy: false,
        sources: ['local', 'url', 'camera'],
        showAdvancedOptions: false,
        maxImageFileSize: 200000000,
        cropping: false,
        multiple: true,
        maxFiles: 10,
        folder: 'uploads',
        defaultSource: 'local',
        eager: [
            {
                crop: 'fit',
                width: 150,
                height: 150,
                gravity: 'auto',
                quality: 'auto',
                format: 'webp'
            }
        ],
        eager_async: false
    }, (error, result) => {
        if (!error && result && result.event === "success") {
            console.log("Upload result:", result.info.secure_url);

             // Get URLs for the original image and the generated thumbnail
            const originalImageUrl = result.info.secure_url; // URL of the original image
            const thumbnailUrl =
                result.info.eager ? result.info.eager[0].secure_url : originalImageUrl; // Use thumbnail if available

            // Update the hidden input field with the original image URL
            const hiddenInput = document.getElementById(hiddenFieldId);
            hiddenInput.value =
                hiddenInput.value ? hiddenInput.value + "," + originalImageUrl : originalImageUrl;

            // Add a thumbnail to the container
            const thumbnailsContainer = document.getElementById(thumbnailsContainerId);
            const thumbnail = document.createElement("img");
            thumbnail.src = thumbnailUrl;
            thumbnail.alt = "Uploaded Image Thumbnail";
            thumbnail.style.maxWidth = "150px";
            thumbnail.style.maxHeight = "150px";
            thumbnail.className = "img-thumbnail m-2";
            thumbnailsContainer.appendChild(thumbnail);
        }
    });

    // Attach the click event listener to the upload button
    document.getElementById(buttonId).addEventListener("click", function () {
        uploadWidget.open();
    }, false);
}

// Export the function for module-based environments
if (typeof module !== 'undefined') {
    module.exports = { initCloudinaryUploadWidget };
}
