// Initialize the map
// var map = L.map('map').setView([51.505, -0.09], 13);
var map = L.map('map', {doubleClickZoom: false}).locate({setView: true, maxZoom: 16});
// Add a tile layer to the map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
// Check if permission is already granted
if ("geolocation" in navigator && !document.cookie.includes('location_permission=granted')) {
    navigator.geolocation.getCurrentPosition(function(position) {
        // If permission is granted, set the cookie
        document.cookie = "location_permission=granted";
        // Use the position data if needed
    });
}

// Add a marker to the map
// L.marker([51.5, -0.09]).addTo(map)
//     .bindPopup('A sample marker!')
//     .openPopup();

var addedKeywords = [];

// Function to add a keyword to the list
function addKeyword() {
    var keywordInput = document.getElementById('keywords');
    var keyword = keywordInput.value.trim();

    if (keyword) {
        addedKeywords.push(keyword);
        keywordInput.value = '';

        // Update the list of added keywords
        var addedKeywordsList = document.getElementById('added-keywords');
        var listItem = document.createElement('li');
        listItem.textContent = keyword;

        // Create a clickable "x" element to remove the keyword
        var removeButton = document.createElement('span');
        removeButton.textContent = ' ×';
        removeButton.className = 'remove-button';
        removeButton.onclick = function() {
            removeKeyword(keyword);
        };
        listItem.appendChild(removeButton);

        addedKeywordsList.appendChild(listItem);

        // Update the hidden input with the list of keywords
        document.getElementById('keywords-list').value = JSON.stringify(addedKeywords);
    }
}

// Function to remove a keyword from the list
function removeKeyword(keyword) {
    addedKeywords = addedKeywords.filter(function(item) {
        return item !== keyword;
    });

    // Update the list of added keywords
    var addedKeywordsList = document.getElementById('added-keywords');
    addedKeywordsList.innerHTML = ''; // Clear the list
    addedKeywords.forEach(function(item) {
        var listItem = document.createElement('li');
        listItem.textContent = item;

        // Create a clickable "x" element to remove the keyword
        var removeButton = document.createElement('span');
        removeButton.textContent = ' ×';
        removeButton.className = 'remove-button';
        removeButton.onclick = function() {
            removeKeyword(item);
        };
        listItem.appendChild(removeButton);

        addedKeywordsList.appendChild(listItem);
    });

    // Update the hidden input with the list of keywords
    document.getElementById('keywords-list').value = JSON.stringify(addedKeywords);
}
// Function to handle form submission
function handleFormSubmission_() {
    // Get the bounding box of the current map extent
    var bounds = map.getBounds();
    var bbox = [bounds.getSouthWest().lng, bounds.getSouthWest().lat, bounds.getNorthEast().lng, bounds.getNorthEast().lat].join(',');

    // Set the value of the hidden input field
    document.getElementById('bbox').value = bbox;

    // Prepare form data
    var formData = new FormData(document.getElementById('data-form'));
    var data = {};
    formData.forEach(function(value, key){
        data[key] = value;
    });

    // Log form data to the console
    console.log(data);
}

// Function to handle form submission
function handleFormSubmission() {
    // Get the bounding box of the current map extent
    var bounds = map.getBounds();
    var bbox = [bounds.getSouthWest().lng, bounds.getSouthWest().lat, bounds.getNorthEast().lng, bounds.getNorthEast().lat].join(',');
    
    // Set the value of the hidden input field
    document.getElementById('bbox').value = bbox;

    // Prepare form data
    var formData = new FormData(document.getElementById('data-form'));
    var data = {};
    formData.forEach(function(value, key){
        if (key === 'keywords_list') {
            // If the key is 'keywords-list', parse the value as JSON
            data[key] = JSON.parse(value);
        } else {
            // Otherwise, use the value as is
            data[key] = value;
        }
    });

    // Convert data to JSON format
    
    var jsonData = JSON.stringify(data);
    console.log('Form data:', jsonData);
    // Send form data as JSON payload using fetch
    fetch('http://localhost:8004/submit-form', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: jsonData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Form data sent successfully:', data);
        // Optionally, do something with the response data
    })
    .catch(error => {
        console.error('There was a problem sending the form data:', error);
    });
}