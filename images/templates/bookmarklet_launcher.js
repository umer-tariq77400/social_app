(function(){
    if(!window.bookmarklet){
        const bookmarklet_js = document.body.appendChild(document.createElement('script'));
        bookmarklet_js.src = `http://localhost:8000/static/js/bookmarklet.js?r=${Math.random() * 999999999}`;
        window.bookmarklet = true;
    }
    else {
        bookmarkletLaunch();
    }
})()