import { render, screen } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router";
import Contact from "../app/pages/Contact";

test("booking form renders labeled inputs", () => {
  const router = createMemoryRouter([{ path: "/", Component: Contact }], {
    initialEntries: ["/"]
  });

  render(<RouterProvider router={router} />);

  expect(screen.getByLabelText(/Full Name/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/Phone Number/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/Event Date & Time/i)).toBeInTheDocument();
});
