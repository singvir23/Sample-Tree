const express = require('express');
const { MongoClient, ServerApiVersion } = require('mongodb');
const dotenv = require('dotenv');
const path = require('path');
const fs = require('fs');

// Debug: Print current directory and file existence
const envPath = path.resolve(__dirname, '../.env');
console.log('Looking for .env file at:', envPath);
console.log('.env file exists:', fs.existsSync(envPath));

// Try to load environment variables
try {
    const result = dotenv.config({ path: envPath });
    if (result.error) {
        throw result.error;
    }
    console.log('Environment variables loaded successfully');
} catch (error) {
    console.error('Failed to load .env file:', error);
    
    // Fallback: Try to set environment variables directly
    if (!process.env.MONGODB_URI) {
        process.env.MONGODB_URI = 'mongodb+srv://viraajsingh:Swager88@sample-tree.skx99.mongodb.net/?retryWrites=true&w=majority&appName=Sample-Tree';
        console.log('Set MONGODB_URI directly as fallback');
    }
}

const songRoutes = require('./routes/songRoutes');

const app = express();
const PORT = process.env.PORT || 3000;

// MongoDB Configuration
const uri = process.env.MONGODB_URI;
if (!uri) {
    console.error('ERROR: MongoDB URI is not defined in environment variables');
    process.exit(1);
}

const client = new MongoClient(uri, {
    serverApi: {
        version: ServerApiVersion.v1,
        strict: true,
        deprecationErrors: true,
    },
    maxPoolSize: 50,
    wtimeoutMS: 2500,
});

// Middleware
app.use(express.json());

async function connectToDatabase() {
    try {
        await client.connect();
        await client.db("admin").command({ ping: 1 });
        console.log("✅ MongoDB connection successful");
        
        app.locals.dbClient = client;
        app.use('/api', songRoutes);
        
        app.listen(PORT, () => {
            console.log(`🚀 Server running on http://localhost:${PORT}`);
        });
    } catch (error) {
        console.error('❌ MongoDB connection error:', error);
        process.exit(1);
    }
}

// Initialize the application
connectToDatabase().catch(console.error);

// Graceful shutdown
process.on('SIGINT', async () => {
    try {
        await client.close();
        console.log('MongoDB connection closed.');
        process.exit(0);
    } catch (error) {
        console.error('Error during shutdown:', error);
        process.exit(1);
    }
});