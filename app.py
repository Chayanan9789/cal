#!/usr/bin/env python3
"""
SCMA115 Calculus Solver - Backend Engine
Powered by Flask & SymPy
Solves Limits, Derivatives, Partial Derivatives, Total Differentials,
Indefinite Integrals, and Definite/Improper Integrals from SCMA115.
"""

import os
import re
import math
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

# Predefined symbols and constants
LOCAL_DICT = {
    'e': sp.E,
    'E': sp.E,
    'pi': sp.pi,
    'PI': sp.pi,
    'oo': sp.oo,
    'inf': sp.oo,
    'infinity': sp.oo,
    'ln': sp.log,
    'log': sp.log,
    'sqrt': sp.sqrt,
    'abs': sp.Abs,
    'sin': sp.sin,
    'cos': sp.cos,
    'tan': sp.tan,
    'csc': sp.csc,
    'sec': sp.sec,
    'cot': sp.cot,
    'asin': sp.asin,
    'acos': sp.acos,
    'atan': sp.atan,
    'arcsin': sp.asin,
    'arccos': sp.acos,
    'arctan': sp.atan,
    'sinh': sp.sinh,
    'cosh': sp.cosh,
    'tanh': sp.tanh,
    'csch': sp.csch,
    'sech': sp.sech,
    'coth': sp.coth,
    'asinh': sp.asinh,
    'acosh': sp.acosh,
    'atanh': sp.atanh,
}

def clean_expression_string(expr_str: str) -> str:
    """Sanitize and normalize raw math input strings."""
    if not expr_str:
        return ""
    s = expr_str.strip()
    # Replace unicode operators and characters
    s = s.replace('−', '-').replace('×', '*').replace('÷', '/').replace('·', '*')
    s = s.replace('π', 'pi').replace('θ', 'theta').replace('∞', 'oo')
    
    # Replace e^x or e^(...) with exp(...)
    s = re.sub(r'\be\^([a-zA-Z0-9_]+)', r'exp(\1)', s)
    s = re.sub(r'\be\^\(', r'exp(', s)
    
    # Replace arc functions
    s = re.sub(r'\barcsin\b', 'asin', s, flags=re.IGNORECASE)
    s = re.sub(r'\barccos\b', 'acos', s, flags=re.IGNORECASE)
    s = re.sub(r'\barctan\b', 'atan', s, flags=re.IGNORECASE)
    s = re.sub(r'\bln\b', 'log', s, flags=re.IGNORECASE)
    return s

def safe_parse(expr_str: str):
    """Safely parse mathematical expression with SymPy."""
    cleaned = clean_expression_string(expr_str)
    if not cleaned:
        raise ValueError("Expression cannot be empty.")
    return parse_expr(cleaned, local_dict=LOCAL_DICT, transformations=TRANSFORMATIONS, evaluate=False)

def parse_bound(bound_str: str, default_val=0):
    """Parse integral or limit bounds like numbers, pi, -oo, oo."""
    if not bound_str or not bound_str.strip():
        return default_val
    b = bound_str.strip()
    if b.lower() in ['oo', 'inf', '+oo', '+inf', 'infinity']:
        return sp.oo
    if b.lower() in ['-oo', '-inf', '-infinity']:
        return -sp.oo
    return safe_parse(b)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "SCMA115 Calculus Solver Engine", "version": "1.0.0"})

@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)

@app.route("/api/preset_handouts", methods=["GET"])
def preset_handouts():
    """Collection of canonical SCMA115 Calculus problems across all syllabus handouts."""
    presets = [
        {
            "category": "limits",
            "title": "Indeterminate Rational Limit (0/0)",
            "expression": "(x^2 - 9) / (x - 3)",
            "var": "x",
            "target": "3",
            "direction": "+-",
            "description": "Factoring technique: factor numerator (x-3)(x+3) and cancel."
        },
        {
            "category": "limits",
            "title": "Trigonometric Limit",
            "expression": "sin(5*x) / x",
            "var": "x",
            "target": "0",
            "direction": "+-",
            "description": "Standard trigonometric limit identity as x approaches 0."
        },
        {
            "category": "limits",
            "title": "One-Sided Limit (Square Root)",
            "expression": "sqrt(x - 2)",
            "var": "x",
            "target": "2",
            "direction": "+",
            "description": "Right-hand limit defined on domain x >= 2."
        },
        {
            "category": "limits",
            "title": "Limit at Infinity (Horizontal Asymptote)",
            "expression": "(3*x^2 + 5*x - 1) / (2*x^2 - 4)",
            "var": "x",
            "target": "oo",
            "direction": "+-",
            "description": "Divide numerator and denominator by highest power x^2."
        },
        {
            "category": "derivatives",
            "title": "Product & Chain Rule Combination",
            "expression": "x^3 * sin(2*x)",
            "var": "x",
            "order": 1,
            "description": "Differentiating product of polynomial and trigonometric composite."
        },
        {
            "category": "derivatives",
            "title": "Quotient Rule & Exponential",
            "expression": "exp(2*x) / (x^2 + 1)",
            "var": "x",
            "order": 1,
            "description": "Quotient rule application with e^(2x)."
        },
        {
            "category": "derivatives",
            "title": "Higher-Order Derivative (Order 2)",
            "expression": "ln(x^2 + 4)",
            "var": "x",
            "order": 2,
            "description": "Second derivative d^2/dx^2 for concavity and inflection points."
        },
        {
            "category": "partial_derivatives",
            "title": "Mixed Partial Derivatives f_xy",
            "expression": "x^3 * y^2 + 2*x * exp(y) - sin(x*y)",
            "var": "x",
            "mixed_vars": "x,y",
            "op_type": "partial",
            "description": "Verifying Clairaut's Theorem: f_xy = d/dy(df/dx)."
        },
        {
            "category": "partial_derivatives",
            "title": "Total Differential df",
            "expression": "sqrt(x^2 + y^2)",
            "var": "x",
            "mixed_vars": "x,y",
            "op_type": "total_diff",
            "description": "Total differential df = (df/dx)dx + (df/dy)dy in multivariable calculus."
        },
        {
            "category": "indefinite_integrals",
            "title": "Integration by Substitution (u-sub)",
            "expression": "x * sqrt(x^2 + 1)",
            "var": "x",
            "description": "Let u = x^2 + 1, du = 2x dx."
        },
        {
            "category": "indefinite_integrals",
            "title": "Integration by Parts",
            "expression": "x * exp(3*x)",
            "var": "x",
            "description": "Integration by parts formula: integral u dv = uv - integral v du."
        },
        {
            "category": "indefinite_integrals",
            "title": "Partial Fraction Decomposition",
            "expression": "(5*x + 3) / (x^2 - 9)",
            "var": "x",
            "description": "Decomposing rational function into A/(x-3) + B/(x+3)."
        },
        {
            "category": "definite_integrals",
            "title": "Definite Integral (Trigonometric Area)",
            "expression": "sin(x)^2",
            "var": "x",
            "lower": "0",
            "upper": "pi",
            "description": "Using half-angle formula (1 - cos(2x))/2 over [0, pi]."
        },
        {
            "category": "definite_integrals",
            "title": "Improper Integral (Infinite Bound)",
            "expression": "exp(-2*x)",
            "var": "x",
            "lower": "0",
            "upper": "oo",
            "description": "Improper integral converging to 1/2 as upper limit approaches oo."
        }
    ]
    return jsonify({"presets": presets})

@app.route("/api/solve", methods=["POST"])
def solve():
    """Main calculation endpoint supporting all 5 categories from SCMA115."""
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"success": False, "error": "Invalid JSON payload."}), 400

    category = data.get("category", "limits").lower().strip()
    raw_expr = data.get("expression", "").strip()
    var_str = data.get("var", "x").strip() or "x"
    lang = data.get("lang", "en").lower().strip()
    is_th = (lang == "th")

    if not raw_expr:
        msg = "กรุณากรอกฟังก์ชันหรือสมการคณิตศาสตร์" if is_th else "Please enter a mathematical expression."
        return jsonify({"success": False, "error": msg}), 400

    try:
        f = safe_parse(raw_expr)
        var = sp.Symbol(var_str)
    except Exception as e:
        msg = f"รูปแบบสมการไม่ถูกต้อง: {str(e)} กรุณาตรวจสอบวงเล็บและเครื่องหมายทางคณิตศาสตร์" if is_th else f"Syntax parsing error: {str(e)}. Please check parentheses and operators."
        return jsonify({
            "success": False,
            "error": msg
        }), 400

    try:
        result_latex = ""
        problem_latex = ""
        steps_info = []
        numeric_val = None

        # -------------------------------------------------------------
        # 1. LIMITS & ONE-SIDED LIMITS
        # -------------------------------------------------------------
        if category in ["limits", "limit"]:
            target_str = data.get("target", "0")
            dir_str = data.get("direction", "+-").strip() # "+", "-", or "+-"
            target_val = parse_bound(target_str, default_val=0)

            # Build problem latex
            dir_sym = ""
            if dir_str == "+":
                dir_sym = "^+"
                sym_dir = '+'
            elif dir_str == "-":
                dir_sym = "^-"
                sym_dir = '-'
            else:
                dir_sym = ""
                sym_dir = '+-'

            t_latex = sp.latex(target_val)
            problem_latex = f"\\lim_{{{sp.latex(var)} \\to {t_latex}{dir_sym}}} \\left( {sp.latex(f)} \\right)"

            try:
                if sym_dir == '+-':
                    ans = sp.limit(f, var, target_val, dir='+-')
                else:
                    ans = sp.limit(f, var, target_val, dir=sym_dir)
            except Exception:
                # Try computing from left and right
                ans_r = sp.limit(f, var, target_val, dir='+')
                ans_l = sp.limit(f, var, target_val, dir='-')
                if sym_dir == '+-':
                    if ans_r == ans_l:
                        ans = ans_r
                    else:
                        ans = sp.Symbol('\\text{Does Not Exist (DNE)}')
                        if is_th:
                            steps_info.append(f"ลิมิตทางซ้าย: {sp.latex(ans_l)}")
                            steps_info.append(f"ลิมิตทางขวา: {sp.latex(ans_r)}")
                            steps_info.append("เนื่องจากลิมิตทางซ้ายและลิมิตทางขวาไม่เท่ากัน ลิมิตสองด้านจึงหาค่าไม่ได้ (DNE)")
                        else:
                            steps_info.append(f"Left-hand limit: {sp.latex(ans_l)}")
                            steps_info.append(f"Right-hand limit: {sp.latex(ans_r)}")
                            steps_info.append("Since left-hand limit != right-hand limit, the two-sided limit does not exist.")
                elif sym_dir == '+':
                    ans = ans_r
                else:
                    ans = ans_l

            ans_simplified = sp.simplify(ans)
            result_latex = sp.latex(ans_simplified)
            
            # Additional limit analysis
            if is_th:
                steps_info.append(f"จุดเป้าหมาย: {var_str} เข้าใกล้ {sp.latex(target_val)}")
                if dir_sym:
                    steps_info.append(f"ทิศทางลิมิตด้านเดียว: จากทาง{'ขวา (ด้านบวก)' if dir_str=='+' else 'ซ้าย (ด้านลบ)'}")
                else:
                    steps_info.append("การประเมิน: ลิมิตสองด้านมาตรฐาน")
            else:
                steps_info.append(f"Target point: {var_str} -> {sp.latex(target_val)}")
                if dir_sym:
                    steps_info.append(f"One-sided direction: from the {'right (positive)' if dir_str=='+' else 'left (negative)'}")
                else:
                    steps_info.append("Evaluation: Standard two-sided limit")

        # -------------------------------------------------------------
        # 2. DERIVATIVES (HIGHER-ORDER, PRODUCT, QUOTIENT, CHAIN RULE)
        # -------------------------------------------------------------
        elif category in ["derivatives", "derivative"]:
            order = int(data.get("order", 1))
            if order < 1:
                order = 1
            if order > 20:
                err_msg = "อันดับอนุพันธ์สูงเกินไป (ไม่เกิน 20)" if is_th else "Order too large (max 20)."
                return jsonify({"success": False, "error": err_msg}), 400

            ans = sp.diff(f, var, order)
            ans_simplified = sp.simplify(ans)

            # Alternate forms (trigsimp, factor)
            alt_trig = sp.trigsimp(ans)
            if alt_trig != ans_simplified and len(str(alt_trig)) < len(str(ans_simplified)):
                ans_simplified = alt_trig

            if order == 1:
                problem_latex = f"\\frac{{d}}{{d{sp.latex(var)}}} \\left[ {sp.latex(f)} \\right]"
            else:
                problem_latex = f"\\frac{{d^{{{order}}}}}{{d{sp.latex(var)}^{{{order}}}}} \\left[ {sp.latex(f)} \\right]"

            result_latex = sp.latex(ans_simplified)
            if is_th:
                steps_info.append(f"หาอนุพันธ์เทียบกับตัวแปร {var_str}, อันดับ {order}")
                if order == 1:
                    steps_info.append("ประยุกต์กฎการหาอนุพันธ์ (กฎกำลัง กฎผลคูณ กฎผลหาร และกฎลูกโซ่)")
                else:
                    steps_info.append(f"หาอนุพันธ์ต่อเนื่อง {order} ครั้งตามลำดับ")
            else:
                steps_info.append(f"Differentiation with respect to {var_str}, order {order}")
                if order == 1:
                    steps_info.append("Applied differential rules (Power, Product, Quotient, and Chain rules).")
                else:
                    steps_info.append(f"Successively differentiated {order} times.")

        # -------------------------------------------------------------
        # 3. PARTIAL DERIVATIVES & TOTAL DIFFERENTIAL
        # -------------------------------------------------------------
        elif category in ["partial_derivatives", "partial", "total_differential"]:
            op_type = data.get("op_type", "partial").strip() # "partial" or "total_diff"
            mixed_str = data.get("mixed_vars", var_str).strip()
            # Split variables: e.g. "x,y" or "x, x, y"
            var_names = [v.strip() for v in re.split(r'[,; ]+', mixed_str) if v.strip()]
            if not var_names:
                var_names = [var_str]

            sym_vars = [sp.Symbol(v) for v in var_names]

            if op_type == "total_diff":
                # Total Differential: df = (df/dx)dx + (df/dy)dy + ...
                free_vars = sorted(list(f.free_symbols), key=lambda s: s.name)
                terms = []
                if is_th:
                    steps_info.append(f"คำนวณอนุพันธ์ย่อยเทียบกับทุกตัวแปรอิสระ: {', '.join([s.name for s in free_vars])}")
                else:
                    steps_info.append(f"Computing partial derivatives with respect to all free variables: {', '.join([s.name for s in free_vars])}")
                for s in free_vars:
                    p_diff = sp.simplify(sp.diff(f, s))
                    terms.append(f"\\left( {sp.latex(p_diff)} \\right) d{sp.latex(s)}")
                    steps_info.append(f"\\frac{{\\partial f}}{{\\partial {sp.latex(s)}}} = {sp.latex(p_diff)}")
                problem_latex = f"d\\left[ {sp.latex(f)} \\right]"
                result_latex = " + ".join(terms) if terms else "0"
            else:
                # Partial differentiation in order of given variables
                ans = f
                for s in sym_vars:
                    ans = sp.diff(ans, s)
                ans_simplified = sp.simplify(ans)

                if len(sym_vars) == 1:
                    problem_latex = f"\\frac{{\\partial}}{{\\partial {sp.latex(sym_vars[0])}}} \\left[ {sp.latex(f)} \\right]"
                else:
                    denom = " ".join([f"\\partial {sp.latex(s)}" for s in sym_vars])
                    problem_latex = f"\\frac{{\\partial^{{{len(sym_vars)}}}}}{{{denom}}} \\left[ {sp.latex(f)} \\right]"

                result_latex = sp.latex(ans_simplified)
                if is_th:
                    steps_info.append(f"หาอนุพันธ์ย่อยตามลำดับตัวแปร: {', '.join([s.name for s in sym_vars])}")
                    steps_info.append("กำหนดให้ตัวแปรอื่น ๆ เสมือนค่าคงตัว (Constant) ในขณะหาอนุพันธ์ย่อยในแต่ละขั้น")
                else:
                    steps_info.append(f"Differentiating partially in sequence: {', '.join([s.name for s in sym_vars])}")
                    steps_info.append("All other variables are treated as constants during each partial derivative.")

        # -------------------------------------------------------------
        # 4. INDEFINITE INTEGRALS (SUBSTITUTION, PARTS, FRACTIONS, TRIG)
        # -------------------------------------------------------------
        elif category in ["indefinite_integrals", "indefinite", "integral"]:
            ans = sp.integrate(f, var)
            ans_simplified = sp.simplify(ans)

            # Check if partial fraction expansion is illuminating
            try:
                if f.is_rational_function(var):
                    pf = sp.apart(f, var)
                    if pf != f:
                        msg = f"การแยกเศษส่วนย่อยของตัวถูกอินทิเกรต: {sp.latex(pf)}" if is_th else f"Partial fraction decomposition of integrand: {sp.latex(pf)}"
                        steps_info.append(msg)
            except Exception:
                pass

            problem_latex = f"\\int \\left( {sp.latex(f)} \\right) d{sp.latex(var)}"
            result_latex = f"{sp.latex(ans_simplified)} + C"
            if is_th:
                steps_info.append(f"หาปฏิยานุพันธ์เทียบกับตัวแปร {var_str} เรียบร้อยแล้ว")
                steps_info.append("บวกค่าคงตัวของการอินทิเกรต (+ C) โดยอัตโนมัติ")
            else:
                steps_info.append(f"Antiderivative found with respect to {var_str}.")
                steps_info.append("Arbitrary constant of integration (+ C) added.")

        # -------------------------------------------------------------
        # 5. DEFINITE & IMPROPER INTEGRALS
        # -------------------------------------------------------------
        elif category in ["definite_integrals", "definite", "improper"]:
            lower_str = data.get("lower", "0")
            upper_str = data.get("upper", "1")
            lower_val = parse_bound(lower_str, default_val=0)
            upper_val = parse_bound(upper_str, default_val=1)

            ans = sp.integrate(f, (var, lower_val, upper_val))
            ans_simplified = sp.simplify(ans)

            problem_latex = f"\\int_{{{sp.latex(lower_val)}}}^{{{sp.latex(upper_val)}}} \\left( {sp.latex(f)} \\right) d{sp.latex(var)}"
            result_latex = sp.latex(ans_simplified)

            # Numeric evaluation if finite
            try:
                num = sp.N(ans_simplified, 6)
                if num.is_number and not num.has(sp.oo) and not num.has(-sp.oo):
                    numeric_val = float(num)
                    approx_txt = f"ค่าประมาณทศนิยม: \\approx {numeric_val:.6g}" if is_th else f"Decimal numerical approximation: \\approx {numeric_val:.6g}"
                    steps_info.append(approx_txt)
            except Exception:
                pass

            is_improper = (lower_val in [sp.oo, -sp.oo]) or (upper_val in [sp.oo, -sp.oo])
            if is_improper:
                steps_info.append("คำนวณปริพันธ์ไม่ตรงแบบโดยใช้ลิมิตของขอบเขต" if is_th else "Improper integral evaluated using limit of bounds.")
            else:
                steps_info.append("ประยุกต์ทฤษฎีบทหลักมูลของแคลคูลัส (Fundamental Theorem): F(b) - F(a)" if is_th else "Fundamental Theorem of Calculus applied: F(b) - F(a).")

        else:
            return jsonify({
                "success": False,
                "error": f"Unknown category '{category}'. Choose from: limits, derivatives, partial_derivatives, indefinite_integrals, definite_integrals."
            }), 400

        return jsonify({
            "success": True,
            "category": category,
            "expression_raw": raw_expr,
            "problem_latex": problem_latex,
            "result_latex": result_latex,
            "steps": steps_info,
            "numeric_value": numeric_val,
            "sympy_str": str(ans_simplified if 'ans_simplified' in locals() else '')
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Calculus computation error: {str(e)}"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
