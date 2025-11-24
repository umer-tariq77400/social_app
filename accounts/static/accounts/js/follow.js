document.addEventListener('alpine:init', () => {
    Alpine.data('followLogic', (initialFollowing, userId, initialFollowers = null) => ({
        following: initialFollowing,
        followersCount: initialFollowers,
        loading: false,
        
        toggleFollow() {
            if (this.loading) return;
            this.loading = true;
            const action = this.following ? 'unfollow' : 'follow';
            const formData = new FormData();
            formData.append('id', userId);
            formData.append('action', action);
            
            fetch(document.body.dataset.followUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': Cookies.get('csrftoken')
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    this.following = !this.following;
                    if (this.followersCount !== null) {
                        this.followersCount += this.following ? 1 : -1;
                    }
                }
                this.loading = false;
            })
            .catch(error => {
                console.error('Error:', error);
                this.loading = false;
            });
        }
    }));
});
