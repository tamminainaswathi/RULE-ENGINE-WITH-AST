# api/app.py
import sys
import os
import mysql.connector
from flask import Flask, request, jsonify

# Add the backend directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from ast_engine import create_rule, combine_rules, evaluate_rule  # Import the functions from backend

app = Flask(__name__)

# Database connection parameters
DB_CONFIG = {
    'user': 'root',      # Replace with your database username
    'password': 'admin',  # Replace with your database password
    'host': 'localhost',          # Typically localhost for local development
    'database': 'rule_engine'   # Replace with your database name
}

# Create a function to establish a database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/create_rule', methods=['POST'])
def create_rule_endpoint():
    rule_string = request.json['rule']
    ast = create_rule(rule_string)
    
    # Store the rule in the database
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO rules (rule_string) VALUES (%s)", (rule_string,))
    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({"ast": ast.to_dict()})  # Use to_dict() method

@app.route('/combine_rules', methods=['POST'])
def combine_rules_endpoint():
    try:
        rules = request.json['rules']
        operator = request.json.get('operator', 'AND')
        ast = combine_rules([create_rule(r) for r in rules], operator)
        return jsonify({"ast": ast.to_dict()})  # Ensure ast is serialized correctly
    except Exception as e:
        return jsonify({"error": str(e)}), 400  # Return error if something goes wrong

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_endpoint():
    ast = request.json['ast']
    data = request.json['data']
    result = evaluate_rule(ast, data)
    return jsonify({"result": result})

# Endpoint to retrieve all rules from the database
@app.route('/get_rules', methods=['GET'])
def get_rules():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT rule_string FROM rules")
    rules = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return jsonify({"rules": [rule[0] for rule in rules]})

if __name__ == '__main__':
    app.run(debug=True)


