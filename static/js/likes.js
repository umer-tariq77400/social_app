document.addEventListener('alpine:init', () => {
    Alpine.data('imageLike', (imageId, initialAction, initialLikes) => ({
        action: initialAction,
        likes: initialLikes,
        loading: false,
        
        get likeUrl() {
            return document.body.dataset.likeUrl;
        },

        toggleLike() {
            if (this.loading || !this.likeUrl) return;
            this.loading = true;

            const formData = new FormData();
            formData.append('id', imageId);
            formData.append('action', this.action);

            fetch(this.likeUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': Cookies.get('csrftoken'),
                },
                mode: 'same-origin',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    const previousAction = this.action;
                    this.action = previousAction === 'like' ? 'unlike' : 'like';
                    this.likes = previousAction === 'like' ? this.likes + 1 : Math.max(0, this.likes - 1);
                }
            })
            .catch(error => console.error('Error:', error))
            .finally(() => {
                this.loading = false;
            });
        }
    }));
});
