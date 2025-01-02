// document.addEventListener('DOMContentLoaded', function() {
//     // const fileInput = document.querySelector('input[type="file"]');  //if need
//     const fileInput = document.getElementById('id_image');
//     let selectedFiles = [];
//
//     if (fileInput) {
//         const fileListDiv = document.createElement('div');
//         fileInput.parentNode.insertBefore(fileListDiv, fileInput.nextSibling);
//
//         fileInput.addEventListener('change', function(event) {
//             const newFiles = Array.from(fileInput.files);
//
//             selectedFiles = selectedFiles.concat(newFiles);
//
//             fileListDiv.innerHTML = '';
//             selectedFiles.forEach(file => {
//                 const fileItem = document.createElement('p');
//                 fileItem.textContent = file.name;
//                 fileListDiv.appendChild(fileItem);
//             });
//
//             fileInput.value = '';
//         });
//
//         const form = document.querySelector('form');
//         form.addEventListener('submit', function(event) {
//             const dataTransfer = new DataTransfer();
//
//             selectedFiles.forEach(file => {
//                 dataTransfer.items.add(file);
//             });
//
//             fileInput.files = dataTransfer.files;
//         });
//     }
// });
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('#id_image');
    const fileList = document.querySelector('#file-list');

    fileInput.addEventListener('change', function(event) {
        fileList.innerHTML = ''; // Очистить список файлов.

        Array.from(event.target.files).forEach(file => {
            const listItem = document.createElement('li');
            listItem.textContent = file.name;
            fileList.appendChild(listItem);
        });
    });
});
