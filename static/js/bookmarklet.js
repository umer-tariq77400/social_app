const siteUrl = "http://localhost:8000/";
const styleUrl = siteUrl + "static/css/bookmarklet.css";
const minWidth = 100;
const minHeight = 100;

// Load CSS
var head = document.getElementsByTagName('head')[0]; 
var link = document.createElement('link'); 
link.rel = 'stylesheet';
link.type = 'text/css';
link.href = styleUrl + '?r=' + Math.random()*999999999;
head.appendChild(link);

// Load HTML
var body = document.getElementsByTagName('body')[0];
var boxHtml = `
<div id="bookmarklet">
 <a href="#" id="close">&times;</a>
 <h1>Select an image to bookmark:</h1>
 <div class="images"></div>
</div>`;
body.innerHTML += boxHtml;


// Find images in the DOM with min dimensions
function populateImages(imagesFound, imagesContainer) {
    
    imagesFound.forEach(image => {
        // Try multiple sources for image URL
        var imageUrl = null;
        
        // Try src first
        if(image.src && image.src.length > 0) {
            imageUrl = image.src;
        }
        // Try srcset
        else if(image.srcset && image.srcset.length > 0) {
            // Parse srcset and get the first (or best) image
            var srcsetArray = image.srcset.split(',');
            imageUrl = srcsetArray[0].trim().split(' ')[0];
        }
        // Try data-src (lazy loading)
        else if(image.dataset.src && image.dataset.src.length > 0) {
            imageUrl = image.dataset.src;
        }
        
        if(imageUrl) {
            // Get dimensions - wait a bit for naturalWidth to be available
            var width = image.naturalWidth || image.width || 100;
            var height = image.naturalHeight || image.height || 100;
            
            if(width >= minWidth && height >= minHeight) {
                var imageFound = document.createElement('img');
                imageFound.src = imageUrl;
                imageFound.dataset.url = imageUrl;
                imageFound.style.cursor = 'pointer';
                imagesContainer.appendChild(imageFound);
                
                // Add click handler to select/deselect image
                imageFound.addEventListener('click', function(e){
                    this.classList.toggle('selected');
                    e.preventDefault();
                });
            }
        }
    });
    return imagesContainer.querySelectorAll('img');
}

// Image selection functionality
function selectImage(imagesContainer, bookmarklet) {
    imagesContainer.forEach(image => {
        image.addEventListener('click', function(e){
            const imageSelected = e.target;
            bookmarklet.style.display = 'none';
            // Sending selected image URL to server along with the user
            window.open(
                siteUrl 
                + 'images/create/?url=' 
                + encodeURIComponent(imageSelected.dataset.url)
                + '&title=' 
                + encodeURIComponent(document.title), '_blank'
            );
            e.preventDefault();
        })
    })
}


function bookmarkletLaunch(){
    let bookmarklet = document.getElementById('bookmarklet');

    // Clear previous images
    let imagesContainer = bookmarklet.querySelector('.images');
    imagesContainer.innerHTML = '';

    let imagesFound = document.querySelectorAll('img');

    // Display bookmarklet
    bookmarklet.style.display = 'block';

    // Close event
    bookmarklet.querySelector('#close').addEventListener('click', function(e){
        bookmarklet.style.display = 'none';
        e.preventDefault();
    });

    // Find images initially
    imagesContainer = populateImages(imagesFound, imagesContainer);

    // select Image
    selectImage(imagesContainer, bookmarklet);
}

// Launch bookmarklet
bookmarkletLaunch();