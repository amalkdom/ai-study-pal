@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        age = request.form.get("age")
        class_level = request.form.get("class_level")
        email = request.form.get("email")
        password = request.form.get("password")

        # convert age to integer safely
        try:
            age = int(age)
        except:
            age = None

        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            age=age,
            class_level=class_level,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for("main.dashboard"))

    return render_template("register.html")
