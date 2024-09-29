const express = require('express');
const path = require('path');
const { spawn } = require('child_process');

const app = express();
const port = 3001;

// Middleware to parse JSON data
const bodyParser = require('body-parser');
const PythonShell = require('python-shell').PythonShell;


// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public'))); // Serve static files

// Set view engine to EJS
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Route for the main page
app.get('/', (req, res) => {
    res.render('index', { diagnosis: null, treatment: [] });
});

// Mock data for diagnosis and treatment
// const sampleData = {
//     diagnosis: "Possible health issue identified.",
//     treatment: [{"Category": "Cardiology", "Treatments": [{"description": "ACE inhibitors", "score": "0.00"}, {"description": "Beta-blockers", "score": "0.20"}]}, {"Category": "Cardiology", "Treatments": [{"description": "ACE inhibitors", "score": "0.00"}, {"description": "Beta-blockers", "score": "0.00"}]}, {"Category": "Pulmonology", "Treatments": [{"description": "Inhaled corticosteroids", "score": "0.00"}, {"description": "Bronchodilators", "score": "0.00"}]}]
// };

// Route to handle data collection and response
app.post('/submit', (req, res) => {
    const { age, gender, history, symptoms } = req.body;

    let prompt_input = `Patient: Age: ${age}-year-old , gender: ${gender} with a, history: ${history}. Symptoms: Currently experiencing ${symptoms}.`
    const pyProg = spawn('python', ['./llm_model.py', '--input', prompt_input]);
    let sampleData;

    pyProg.stdout.on('data', function(data) {
        let a = data.toString()
        let jsonString = a.replace(/'/g, '"');
        sampleData = JSON.parse(jsonString);
        console.log(sampleData);
        
        return res.render('index', {
            diagnosis: 'Possible health issue identified.',
            treatment: sampleData
        });

    });

    // const { age, gender, notes } = req.body;
    // // Here you would normally call the Python LLM
    // // For now, we'll send back the sample data
    // if (age && gender) {
    //     return res.render('index', {
    //         diagnosis: sampleData.diagnosis,
    //         treatment: sampleData.treatment
    //     });
    // }
    // else {

    //     res.render('index', {
    //         diagnosis: null,
    //         treatment: []
    //     });
    // }
});



// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
