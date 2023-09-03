self.addEventListener('push', function(event) {
    const options = {
        body: event.data.text(),
        icon: '/static/images/logo.svg', 
    };

    event.waitUntil(
        self.registration.showNotification('Push Notification', options)
    );
});
