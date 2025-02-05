import DialogTitle from "@mui/material/DialogTitle";
import { Button, Card, TextField } from "@mui/material";
import { useState } from "react";
import { useAuth } from "./AuthProvider";
import { useLocation, useNavigate } from "react-router";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const location = useLocation();
  const auth = useAuth();

  function handleSubmit(e) {
    e.preventDefault();
    auth.signin(username, password, () => {
      // Send them back to the page they tried to visit when they were
      // redirected to the login page. Use { replace: true } so we don't create
      // another entry in the history stack for the login page.  This means that
      // when they get to the protected page and click the back button, they
      // won't end up back on the login page, which is also really nice for the
      // user experience.
      const from = location.state?.from?.pathname || "/";

      navigate(from, { replace: true });
    });
  }

  return (
    <Card className="w-1/3 mx-auto mt-10 p-4">
      <DialogTitle className="text-center">EpiSuS Login</DialogTitle>
      <form className=" flex flex-col items-center" onSubmit={handleSubmit}>
        <div className="my-2">
          <TextField
            id="outlined-username"
            label="Username"
            onChange={(event) => {
              setUsername(event.target.value);
            }}
            InputLabelProps={{
              shrink: true,
            }}
          />
        </div>
        <div className="mb-3">
          <TextField
            id="outlined-password"
            label="Password"
            type="password"
            onChange={(event) => {
              setPassword(event.target.value);
            }}
            InputLabelProps={{
              shrink: true,
            }}
          />
        </div>
        <Button type="submit" variant="contained">
          Login
        </Button>
      </form>
    </Card>
  );
}
