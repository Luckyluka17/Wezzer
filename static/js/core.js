function reloadImageTwice(imageId) {
    const img = document.getElementById(imageId);
    const src = img.src;
    img.src = ''; // First set to empty
    img.src = src; // Then set to original src
}