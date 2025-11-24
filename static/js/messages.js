// JavaScript to handle message dismissal

function fadeOutMessage(msg) {
    msg.classList.add('fade-out');
    setTimeout(function() {
        msg.remove();
    }, 300); // Match CSS transition duration
}

document.addEventListener('DOMContentLoaded', function() {
    // Handle close button clicks
    document.querySelectorAll('.messages .close').forEach(function(closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            fadeOutMessage(this.closest('li'));
        });
    });
    
    // Auto-dismiss messages after 5 seconds
    document.querySelectorAll('.messages li').forEach(function(msg) {
        setTimeout(function() {
            fadeOutMessage(msg);
        }, 5000);
    });
});
