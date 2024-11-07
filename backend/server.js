const express = require('express');
const { MongoClient, ServerApiVersion } = require('mongodb');
const dotenv = require('dotenv');
const songRoutes = require('./routes/songRoutes');

dotenv.config({ path: 'backend/.env' }); // Load environment variables

const app = express();
const PORT = process.env.PORT || 3000;

// MongoDB URI from the .env file
const uri = process.env.MONGO_URI;

// Create a MongoClient with the MongoClientOptions object
const client = new MongoClient(uri, {
    serverApi: {
        version: ServerApiVersion.v1,
        strict: true,
        deprecationErrors: true,
    },
});

async function connectToDatabase() {
    try {
        // Connect the client to the server
        await client.connect();
        
        // Ping the database to confirm connection
        await client.db("admin").command({ ping: 1 });
        console.log("Pinged your deployment. You successfully connected to MongoDB!");

        // Pass the MongoDB client to routes or other parts of the app
        app.locals.dbClient = client;

        // Start the Express server only after a successful MongoDB connection
        app.listen(PORT, () => {
            console.log(`Server is running on http://localhost:${PORT}`);
        });

    } catch (err) {
        console.error('Failed to connect to MongoDB:', err);
        process.exit(1); // Exit if there’s a connection error
    }
}

// Call the function to connect to the database
connectToDatabase();

app.use(express.json());
app.use('/api', songRoutes);

// Optional: Close the MongoDB client when the process ends
process.on('SIGINT', async () => {
    await client.close();
    console.log('MongoDB connection closed');
    process.exit(0);
});
