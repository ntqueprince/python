from flask import Flask, render_template, request, jsonify
from decimal import Decimal, InvalidOperation
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CalculatorEngine:
    """
    Handles all mathematical operations with precision and error handling.
    Uses Decimal for accurate floating-point arithmetic.
    """
    
    OPERATORS = {
        '+': lambda a, b: a + b,
        '−': lambda a, b: a - b,
        '×': lambda a, b: a * b,
        '÷': lambda a, b: a / b if b != 0 else None,
    }
    
    @staticmethod
    def calculate(num1_str, num2_str, operator):
        """
        Performs calculation with comprehensive error handling.
        
        Args:
            num1_str: First number as string
            num2_str: Second number as string
            operator: Operation symbol (+, −, ×, ÷)
            
        Returns:
            dict: {'success': bool, 'result': float or None, 'error': str or None}
        """
        try:
            # Validate operator
            if operator not in CalculatorEngine.OPERATORS:
                return {
                    'success': False,
                    'result': None,
                    'error': f'Invalid operator: {operator}'
                }
            
            # Parse and validate inputs
            try:
                num1 = Decimal(str(num1_str).strip())
                num2 = Decimal(str(num2_str).strip())
            except (InvalidOperation, ValueError):
                return {
                    'success': False,
                    'result': None,
                    'error': 'Please enter valid numbers'
                }
            
            # Division by zero check
            if operator == '÷' and num2 == 0:
                return {
                    'success': False,
                    'result': None,
                    'error': 'Cannot divide by zero'
                }
            
            # Perform calculation
            operation = CalculatorEngine.OPERATORS[operator]
            result = operation(num1, num2)
            
            # Convert to float for JSON serialization
            result_float = float(result)
            
            # Format result: remove unnecessary decimals
            if result_float == int(result_float):
                result_formatted = int(result_float)
            else:
                result_formatted = round(result_float, 10)
            
            logger.info(f'Calculation: {num1} {operator} {num2} = {result_formatted}')
            
            return {
                'success': True,
                'result': result_formatted,
                'error': None
            }
            
        except Exception as e:
            logger.error(f'Unexpected error: {str(e)}')
            return {
                'success': False,
                'result': None,
                'error': 'An unexpected error occurred'
            }


@app.route('/')
def index():
    """Renders the calculator UI."""
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    """
    API endpoint for calculations.
    Expects JSON: {'num1': str, 'num2': str, 'operator': str}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        num1 = data.get('num1', '').strip()
        num2 = data.get('num2', '').strip()
        operator = data.get('operator', '').strip()
        
        # Validate required fields
        if not all([num1, num2, operator]):
            return jsonify({
                'success': False,
                'error': 'Please fill all fields'
            }), 400
        
        # Perform calculation
        result = CalculatorEngine.calculate(num1, num2, operator)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f'API error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Server error'}), 500


if __name__ == '__main__':
    # Development server with auto-reload and debugger
    app.run(debug=True, host='localhost', port=5000)