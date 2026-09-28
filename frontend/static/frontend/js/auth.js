async function login(username, password) {

 
const response = await fetch("/api/auth/login/", {
    method: "POST",

    headers: {
        "Content-Type": "application/json"
    },

    body: JSON.stringify({
        username: username,
        password: password
    })
});

const data = await response.json();

if (!response.ok) {
    throw new Error(data.error || "Login failed");
}

localStorage.setItem("access_token", data.access);
localStorage.setItem("refresh_token", data.refresh);

return data;
 

}

async function refreshAccessToken() {

 
const refreshToken = localStorage.getItem("refresh_token");

if (!refreshToken) {
    return false;
}

try {

    const response = await fetch("/api/auth/refresh/", {
        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            refresh: refreshToken
        })
    });

    const data = await response.json();

    if (!response.ok) {
        logout();
        return false;
    }

    localStorage.setItem("access_token", data.access);

    return true;

} catch (error) {

    logout();
    return false;
}
 

}

async function authenticatedFetch(url, options = {}) {

 
let accessToken = localStorage.getItem("access_token");

if (!accessToken) {
    window.location.href = "/login/";
    return;
}

if (!options.headers) {
    options.headers = {};
}

options.headers["Authorization"] = `Bearer ${accessToken}`;

let response = await fetch(url, options);

if (response.status === 401) {

    const refreshed = await refreshAccessToken();

    if (!refreshed) {
        return response;
    }

    accessToken = localStorage.getItem("access_token");

    options.headers["Authorization"] = `Bearer ${accessToken}`;

    response = await fetch(url, options);
}

return response;
 

}

function getAccessToken() {

 
return localStorage.getItem("access_token");
 

}

function getRefreshToken() {

 
return localStorage.getItem("refresh_token");
 

}

function logout() {

 
localStorage.removeItem("access_token");
localStorage.removeItem("refresh_token");

window.location.href = "/login/";
 

}
