const express = require('express');
const session = require('express-session');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');

const app = express();
const PORT = 3000;

// Setup SQLite database
const dbFile = './database.sqlite';
const dbExists = fs.existsSync(dbFile);
const db = new sqlite3.Database(dbFile);

db.serialize(() => {
  if (!dbExists) {
    db.run(`CREATE TABLE users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE,
      password TEXT,
      role TEXT
    )`);

    db.run(`CREATE TABLE products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT,
      description TEXT,
      price_suggested REAL,
      price_affiliate REAL,
      images TEXT,
      published_by INTEGER,
      published INTEGER DEFAULT 0,
      FOREIGN KEY(published_by) REFERENCES users(id)
    )`);

    // Insert default users with hashed passwords
    const insertUser = db.prepare('INSERT INTO users (username, password, role) VALUES (?, ?, ?)');
    const saltRounds = 10;
    const users = [
      { username: 'master', password: 'master123', role: 'master' },
      { username: 'supervisor', password: 'supervisor123', role: 'supervisor' },
      { username: 'afiliado', password: 'afiliado123', role: 'afiliado' }
    ];
    users.forEach(user => {
      const hash = bcrypt.hashSync(user.password, saltRounds);
      insertUser.run(user.username, hash, user.role);
    });
    insertUser.finalize();
  }
});

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(session({
  secret: 'secret-key',
  resave: false,
  saveUninitialized: false
}));

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Multer setup for image uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadDir = path.join(__dirname, 'uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir);
    }
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + path.extname(file.originalname));
  }
});
const upload = multer({ storage: storage });

// Authentication middleware
function requireLogin(req, res, next) {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
}

// Routes

// Login
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  db.get('SELECT * FROM users WHERE username = ?', [username], (err, user) => {
    if (err) return res.status(500).json({ error: 'Database error' });
    if (!user) return res.status(401).json({ error: 'Invalid credentials' });
    if (!bcrypt.compareSync(password, user.password)) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    req.session.userId = user.id;
    req.session.role = user.role;
    req.session.username = user.username;
    res.json({ message: 'Login successful', role: user.role });
  });
});

// Logout
app.post('/api/logout', (req, res) => {
  req.session.destroy();
  res.json({ message: 'Logged out' });
});

// Get current user info
app.get('/api/me', (req, res) => {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  res.json({ id: req.session.userId, username: req.session.username, role: req.session.role });
});

// Create user (only master)
app.post('/api/users', requireLogin, (req, res) => {
  if (req.session.role !== 'master') {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const { username, password, role } = req.body;
  if (!username || !password || !role) {
    return res.status(400).json({ error: 'Missing fields' });
  }
  const hash = bcrypt.hashSync(password, 10);
  db.run('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', [username, hash, role], function(err) {
    if (err) {
      if (err.code === 'SQLITE_CONSTRAINT') {
        return res.status(409).json({ error: 'User already exists' });
      }
      return res.status(500).json({ error: 'Database error' });
    }
    res.json({ id: this.lastID, username, role });
  });
});

// List users (only master)
app.get('/api/users', requireLogin, (req, res) => {
  if (req.session.role !== 'master') {
    return res.status(403).json({ error: 'Forbidden' });
  }
  db.all('SELECT id, username, role FROM users', (err, rows) => {
    if (err) return res.status(500).json({ error: 'Database error' });
    res.json(rows);
  });
});

// Delete user (only master)
app.delete('/api/users/:id', requireLogin, (req, res) => {
  if (req.session.role !== 'master') {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const userId = req.params.id;
  db.run('DELETE FROM users WHERE id = ?', [userId], function(err) {
    if (err) return res.status(500).json({ error: 'Database error' });
    if (this.changes === 0) return res.status(404).json({ error: 'User not found' });
    res.json({ message: 'User deleted' });
  });
});

// Create product (master and supervisor)
app.post('/api/products', requireLogin, upload.array('images', 5), (req, res) => {
  if (!['master', 'supervisor'].includes(req.session.role)) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const { name, description, price_suggested, price_affiliate } = req.body;
  if (!name || !description || !price_suggested || !price_affiliate) {
    return res.status(400).json({ error: 'Missing fields' });
  }
  if (parseFloat(price_suggested) <= parseFloat(price_affiliate)) {
    return res.status(400).json({ error: 'Precio sugerido debe ser mayor que precio para afiliado' });
  }
  const images = req.files.map(file => file.filename).join(',');
  db.run(
    'INSERT INTO products (name, description, price_suggested, price_affiliate, images, published_by) VALUES (?, ?, ?, ?, ?, ?)',
    [name, description, price_suggested, price_affiliate, images, req.session.userId],
    function(err) {
      if (err) return res.status(500).json({ error: 'Database error' });
      res.json({ id: this.lastID, name, description, price_suggested, price_affiliate, images });
    }
  );
});

// List products (all roles)
app.get('/api/products', requireLogin, (req, res) => {
  db.all('SELECT * FROM products', (err, rows) => {
    if (err) return res.status(500).json({ error: 'Database error' });
    res.json(rows);
  });
});

// Mark product as published (affiliate)
app.post('/api/products/:id/publish', requireLogin, (req, res) => {
  if (req.session.role !== 'afiliado') {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const productId = req.params.id;
  db.run('UPDATE products SET published = 1 WHERE id = ?', [productId], function(err) {
    if (err) return res.status(500).json({ error: 'Database error' });
    if (this.changes === 0) return res.status(404).json({ error: 'Product not found' });
    res.json({ message: 'Product marked as published' });
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
