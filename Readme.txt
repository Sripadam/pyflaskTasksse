improved  handling routes
Non blocking notification using  Threding
implemented real time SSE updates for frontend RxJS integration
Refracted code for better performance & maintainability

//Clients can subscribe to /events to receive instant updates when tasks change
// used Server-Sent Events (SSE) for Efficient one-way streaming

const eventSource = new EventSource("http://127.0.0.1:5000/events");
eventSource.onmessage = function(event) {
    console.log("New Update:", event.data);
};
