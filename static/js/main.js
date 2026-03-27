// Modal Message Functions
    function closeMessageModal() {
        const modal = document.getElementById('messageModal');
        if (modal) {
            modal.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => {
                modal.remove();
            }, 500);
        }
    }