(function(){
    if(!window.bookmarklet){
        const bookmarklet_js = document.body.appendChild(document.createElement('script'));
        bookmarklet_js.src = `https://docker-app-9a76b3f1350c.herokuapp.com/static/js/bookmarklet.js?r=${Math.random() * 999999999}`;
        window.bookmarklet = true;
    }
    else {
        bookmarkletLaunch();
    }
})()