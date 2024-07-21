function reloadImage(img) {
    let originalSrc = img.src;
    img.src = '';
    img.src = originalSrc;
}

function reloadImages(times) {
    let images = document.querySelectorAll('img');
    for (let i = 0; i < times; i++) {
        images.forEach(function(img) {
            reloadImage(img);
        });
    }
}

function getLocationAndRedirect() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            window.location.href = `/set_location?cityname=Votre position&longitude=${longitude}&latitude=${latitude}`;
        }, function(error) {
            alert('Erreur lors de la récupération de la localisation: ' + error.message);
        });
    } else {
        alert('La géolocalisation n\'est pas supportée par ce navigateur.');
    }
}