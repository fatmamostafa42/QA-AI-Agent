from app.generators.scenario_intelligence import ScenarioIntelligence

engine = ScenarioIntelligence()

tests = [

    "Create User",

    "Edit Employee",

    "Delete Candidate",

    "Search Leave",

    "Approve Leave",

    "Assign Claim",

    "Upload Logo",

    "Reset Password",

    "Login",

    "Logout"

]

for t in tests:

    print(t)

    print(engine.analyze(t))

    print("-" * 40)