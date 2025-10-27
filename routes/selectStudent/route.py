import os
import subprocess
from flask import Blueprint, jsonify
import sys

selectStudent_bp = Blueprint("selectStudent_bp", __name__)

@selectStudent_bp.route("/run-selectStudent", methods=["GET", "POST"])
def run_selectStudent():
    print("Hello Select Student Route")
    return ({"message" : "Running the selection Student"}) , 200