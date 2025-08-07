let ws;
let loginAttemptUser = null;
let pendingAction;
let currentUser = null;

function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time));
}

function showMessage(msg) {
    document.getElementById('message').textContent = msg;
}

function loadMoneyFromSocket(user) {
    ws.send(JSON.stringify({ type: 'get_balance', user: user }));
}

function updateBalance(balance) {
    delay(1000);
    document.getElementById("balance").textContent = balance;
}

function showLoggedIn(username) {
    document.getElementById('USERNAME').textContent = 'Logged in as: ' + username;
    document.getElementById('logoutBtn').style.display = 'inline-block';
    localStorage.setItem('currentUser', username);
}

function connectWebSocket() {
    ws = new WebSocket('ws://127.0.0.1:6509');
    ws.onopen = function () {
        console.log('Websocket connected');
    };
    ws.onmessage = function (event) {
        let data;
        try {
            data = JSON.parse(event.data);
        } catch {
            console.log(event.data);
            return;
        }
        if (data.type === 'login_result' && pendingAction === 'login') {
            if (data.success) {
                currentUser = loginAttemptUser;
                console.log(currentUser);
                showLoggedIn(currentUser);
                loadMoneyFromSocket(currentUser)
            } else {
                console.log("Login failed");
            }
            pendingAction = null;
            loginAttemptUser = null;
        } else if (data.type === 'server_balance') {
            if (data.success) {
                balance = data.balance;
                newbalance = data.balance;
                updateBalance(newbalance);
            }
        }
    };
};
connectWebSocket();
document.getElementById('loginForm').onsubmit = function (e) {
    e.preventDefault();
    const usr = document.getElementById('login_usr').value;
    const pwd = document.getElementById('login_pwd').value;
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'login', user: usr, password: pwd }));
        pendingAction = 'login';
        loginAttemptUser = usr;
    }
    document.getElementById('loginForm').reset();
};

document.getElementById('logoutBtn').onclick = function () {
    currentUser = null;
    document.getElementById('USERNAME').textContent = '';
    document.getElementById('logoutBtn').style.display = 'none';
    localStorage.removeItem('currentUser');
}

document.getElementById('CashToSocket').onclick = function () {
    let spanbalanceelement = document.getElementById('balance');
    let balance = spanbalanceelement.textContent;
    if (ws && ws.readyState === WebSocket.OPEN && currentUser) {
        ws.send(JSON.stringify({ type: 'update_balance', user: currentUser, balance: balance }));
    } else {
        console.log("Websocket not connected");
    }
}

window.onload = function () {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = savedUser;
        showLoggedIn(currentUser);
        delay(1000).then(() => {
            if (ws && ws.readyState === WebSocket.OPEN && currentUser) {
                loadMoneyFromSocket(currentUser);
            } else {
                console.log("Websocket Not Connected");
            }
        });


    }
};