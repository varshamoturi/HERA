const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const csv = require('csv-writer').createObjectCsvWriter;

app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

const credentialsPath = path.join(__dirname, 'data/credentials.json');
let credentials = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));

const csvWriter = csv({
    path: 'data/data.csv',
    append: true,
    header: [
        // Header IDs should match the 'name' attributes of the form inputs
        { id: 'name', title: 'Name' },
        { id: 'dob', title: 'Date of Birth' },
        { id: 'gender', title: 'Gender' },
        { id: 'address', title: 'Address' },
        { id: 'email', title: 'Email' },
        { id: 'phone_number', title: 'Phone Number' },
        { id: 'relationship', title: 'Relationship Status' },
        { id: 'parent', title: 'Are you a Parent?' },
        { id: 'occupation', title: 'Occupation' },
        { id: 'education', title: 'Education Level' },
        { id: 'hobbies', title: 'Hobbies/Interests' },
        { id: 'preferredLocation', title: 'Preferred Locations for Matches/Events' },
        { id: 'username', title: 'Username' },
        { id: 'password', title: 'Password' }, // Again, don't store plain text passwords
        { id: 'city', title: 'City' },
        { id: 'state', title: 'State' },
    ]
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const user = credentials.find(u => u.username === username && u.password === password);
    if (user) {
        res.send('Login successful!');
    } else {
        res.send('Login failed: incorrect username or password.');
    }
});

app.post('/signup', (req, res) => {
    // Combine address fields into one
    const address = `${req.body.address1}, ${req.body.city}, ${req.body.state}`;

    // Process hobbies into a comma-separated string
    const hobbies = Array.isArray(req.body.hobbies) ? req.body.hobbies.join(', ') : req.body.hobbies;

    const newUser = {
        // Match these IDs to the 'name' attributes of the form
        name: req.body.name,
        dob: req.body.dob,
        gender: req.body.gender,
        address: address,
        email: req.body.email,
        phone_number: req.body.phone_number, // Make sure the 'name' attribute in your form is 'phone_number'
        relationship: req.body.relationship,
        parent: req.body.parent,
        occupation: req.body.occupation,
        education: req.body.education,
        hobbies: hobbies,
        preferredLocation: req.body.preferredLocation,
        username: req.body.username,
        password: req.body.password, // Password should be hashed
        city: req.body.city,
        state: req.body.state
    };

    const userExists = credentials.some(u => u.username === req.body.username);

    if (userExists) {
        res.status(409).send('Signup failed: User already exists.');
        return;
    }

    csvWriter.writeRecords([newUser])
        .then(() => {
            // Update credentials array and save it to the credentials.json file
            credentials.push({ username: req.body.username, password: req.body.password }); // Password should be hashed
            fs.writeFileSync(credentialsPath, JSON.stringify(credentials, null, 4));
            res.send('Signup successful!');
        })
        .catch(err => {
            console.error('Error writing to CSV:', err);
            res.status(500).send('Signup failed. Please try again later.');
        });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});