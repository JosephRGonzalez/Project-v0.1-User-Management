// Fetch users count for admins and customers
async function getUserCounts() {
    const response = await fetch('http://localhost:5000/api/users');
    const users = await response.json();
    const admins = users.filter(user => user.role === 'admin').length;
    const customers = users.filter(user => user.role === 'basicuser').length;

    document.getElementById('admin-count').innerText = admins;
    document.getElementById('customer-count').innerText = customers;
}

getUserCounts();
