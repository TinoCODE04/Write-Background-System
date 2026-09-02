import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva("focus-ring inline-flex items-center justify-center gap-2 rounded-xl text-sm font-semibold transition disabled:pointer-events-none disabled:opacity-50", {
  variants: {
    variant: { default: "bg-ink px-4 py-2.5 text-white hover:bg-moss", accent: "bg-lime px-4 py-2.5 text-ink hover:bg-[#d7ff72]", outline: "border border-black/10 bg-white px-4 py-2.5 hover:bg-black/[.04]", ghost: "px-3 py-2 hover:bg-black/[.05]", danger: "bg-red-600 px-4 py-2.5 text-white hover:bg-red-700" },
    size: { default: "h-10", sm: "h-8 text-xs", lg: "h-12 px-6" }
  }, defaultVariants: { variant: "default", size: "default" }
});
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> { asChild?: boolean; }
export function Button({ className, variant, size, asChild = false, ...props }: ButtonProps) {
  const Comp = asChild ? Slot : "button";
  return <Comp className={cn(buttonVariants({ variant, size }), className)} {...props} />;
}

