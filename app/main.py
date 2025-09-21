import os
from flask import Flask, render_template, request, redirect, url_for, abort
from sqlalchemy.orm import scoped_session

from app.db import init_db, SessionLocal, Plan
from app.agent import PlannerAgent


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    init_db()

    # thread-local session
    app.session = scoped_session(SessionLocal)

    @app.teardown_appcontext
    def remove_session(exc=None):
        app.session.remove()

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/plan", methods=["POST"])
    def make_plan():
        goal = request.form.get("goal", "").strip()
        if not goal:
            return redirect(url_for("index"))

        agent = PlannerAgent()
        try:
            out = agent.plan(goal)
        except Exception as e:
            return render_template("index.html", error=f"Planning failed: {e}")

        # persist as JSON + Markdown
        import json
        plan = Plan(
            goal=out["json"]["goal"],
            plan_markdown=out["markdown"],
            plan_json=json.dumps(out["json"], ensure_ascii=False)
        )
        app.session.add(plan)
        app.session.commit()
        return redirect(url_for("view_plan", plan_id=plan.id))

    @app.route("/plan/<int:plan_id>", methods=["GET"])
    def view_plan(plan_id: int):
        plan = app.session.get(Plan, plan_id)
        if not plan:
            abort(404)
        return render_template("plan.html", plan=plan)

    @app.route("/history", methods=["GET"])
    def history():
        plans = app.session.query(Plan).order_by(Plan.created_at.desc()).all()
        return render_template("history.html", plans=plans)

    # ✅ Register markdown filter
    import markdown2
    app.jinja_env.filters["markdown"] = markdown2.markdown

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
