// Worked example: component test (FE-8, FE-13). Queries by role, tests behaviour, includes an axe check.
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "vitest-axe";
import { describe, expect, it, vi } from "vitest";
import { OrderStatusFilter } from "./OrderStatusFilter";

describe("OrderStatusFilter", () => {
  it("calls onChange with the selected status", async () => {
    const onChange = vi.fn();
    render(<OrderStatusFilter value="open" onChange={onChange} />);

    await userEvent.click(screen.getByRole("radio", { name: "Closed" }));

    expect(onChange).toHaveBeenCalledExactlyOnceWith("closed");
  });

  it("marks the current value as checked", () => {
    render(<OrderStatusFilter value="closed" onChange={() => {}} />);
    expect(screen.getByRole("radio", { name: "Closed" })).toBeChecked();
    expect(screen.getByRole("radio", { name: "Open" })).not.toBeChecked();
  });

  it("is operable by keyboard", async () => {
    const onChange = vi.fn();
    render(<OrderStatusFilter value="open" onChange={onChange} />);

    await userEvent.tab();
    await userEvent.keyboard("{ArrowRight}");

    expect(onChange).toHaveBeenCalledWith("closed");
  });

  it("has no accessibility violations", async () => {
    const { container } = render(<OrderStatusFilter value="open" onChange={() => {}} />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
