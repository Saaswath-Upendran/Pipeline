import axios from 'axios';

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();  // Use native trim method
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api', // Base URL for your API
  timeout: 600000, // Timeout in milliseconds
});

// Interceptors for request and response
apiClient.interceptors.request.use(
  (config) => {
    // You can add custom logic here before sending the request
    config.headers = {
      'Content-Type': 'multipart/form-data',
      'X-CSRF-TOKEN': getCookie('csrftoken'), // Important for file uploads
    };
    return config;
  },
  (error) => {
    // Handle request error
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    // You can add custom logic here after receiving the response
    return response;
  },
  (error) => {
    // Handle response error
    return Promise.reject(error);
  }
);

export default apiClient;
