function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    const csrftoken = getCookie('csrftoken');
    const url = document.body.dataset.followUrl;
    var options = {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin'
    }
    
    document.querySelectorAll('a.follow').forEach(button => {
        button.addEventListener('click', function(e){
            e.preventDefault();
            var followButton = this;
            // add request body
            var formData = new FormData();
            formData.append('id', followButton.dataset.id);
            formData.append('action', followButton.dataset.action);
            options['body'] = formData;
            // send HTTP request
            fetch(url, options)
            .then(response => response.json())
            .then(data => {
                if (data['status'] === 'ok')
                {
                    var previousAction = followButton.dataset.action;
                    // toggle button text and data-action
                    var action = previousAction === 'follow' ? 'unfollow' : 'follow';
                    followButton.dataset.action = action;
                    followButton.innerHTML = action === 'follow' 
                        ? '<i class="fas fa-user-plus"></i> Follow' 
                        : '<i class="fas fa-user-check"></i> Following';
                    
                    // Handle different button styles (list vs detail)
                    if (followButton.classList.contains('btn')) {
                        // List view styles
                        if (action === 'follow') {
                            followButton.classList.remove('btn-secondary');
                            followButton.classList.add('btn-primary');
                        } else {
                            followButton.classList.remove('btn-primary');
                            followButton.classList.add('btn-secondary');
                        }
                    } else {
                        // Detail view styles
                        if (action === 'follow') {
                            followButton.classList.remove('unfollow');
                        } else {
                            followButton.classList.add('unfollow');
                        }
                    }
                    
                    // update follower count (List view)
                    var followerCount = followButton.closest('.user-item')?.querySelector('.follower-count strong');
                    if (followerCount) {
                        var totalFollowers = parseInt(followerCount.innerHTML);
                        followerCount.innerHTML = previousAction === 'follow' ? 
                            totalFollowers + 1 : totalFollowers - 1;
                    }

                    // update follower count (Detail view)
                    var followerCountDisplay = document.querySelector('span.followers-count-display');
                    if (followerCountDisplay) {
                        var totalFollowers = parseInt(followerCountDisplay.innerHTML);
                        followerCountDisplay.innerHTML = previousAction === 'follow' ? 
                            totalFollowers + 1 : totalFollowers - 1;
                    }
                    
                    // update stat item (Detail view)
                    var statCount = document.querySelector('.stat-item:nth-child(2) .stat-number');
                    if (statCount) {
                        var count = parseInt(statCount.innerHTML);
                        statCount.innerHTML = previousAction === 'follow' ? 
                            count + 1 : count - 1;
                    }
                }
            })
        });
    });
});
