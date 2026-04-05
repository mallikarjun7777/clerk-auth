"use client";

import { useEffect, useState } from "react";
import { SignInButton, SignUpButton, UserButton, useAuth } from "@clerk/nextjs";

export default function Home() {
  const { isSignedIn, getToken } = useAuth();
  const [status, setStatus] = useState("Sign up or sign in to store your profile.");
  const [savedUser, setSavedUser] = useState<string | null>(null);

  useEffect(() => {
    if (!isSignedIn) {
      setSavedUser(null);
      setStatus("Sign up or sign in to store your profile.");
      return;
    }

    const syncUser = async () => {
      try {
        const token = await getToken();
        const res = await fetch("http://localhost:8000/users/sync", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (!res.ok) {
          const text = await res.text();
          throw new Error(text || res.statusText);
        }

        const data = await res.json();
        setSavedUser(`${data.clerk_id} (${data.email})`);
        setStatus("User verified and stored by backend.");
      } catch (error) {
        setStatus(`Backend sync failed: ${error instanceof Error ? error.message : String(error)}`);
      }
    };

    syncUser();
  }, [isSignedIn, getToken]);

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 dark:bg-black dark:text-zinc-50">
      <main className="mx-auto flex min-h-screen max-w-4xl flex-col items-center justify-center gap-8 px-6 py-16">
        <div className="w-full rounded-3xl bg-white p-10 shadow-xl dark:bg-zinc-950 sm:p-14">
          <div className="flex flex-col gap-6">
            <div>
              <h1 className="text-4xl font-semibold">Clerk Signup with Backend Verification</h1>
              <p className="mt-3 text-base text-zinc-600 dark:text-zinc-300">
                Sign up or sign in with Clerk, then the frontend sends the Clerk token to your FastAPI backend to verify and store the user.
              </p>
            </div>

            <div className="flex flex-wrap gap-4">
              <SignUpButton>
                <button className="rounded-full bg-violet-700 px-6 py-3 text-sm font-semibold text-white transition hover:bg-violet-600">
                  Sign Up
                </button>
              </SignUpButton>
              <SignInButton>
                <button className="rounded-full border border-zinc-300 px-6 py-3 text-sm font-semibold transition hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900">
                  Sign In
                </button>
              </SignInButton>
              {isSignedIn && (
                <div className="rounded-full border border-zinc-200 p-1 dark:border-zinc-700">
                  <UserButton />
                </div>
              )}
            </div>

            <div className="rounded-3xl border border-zinc-200 bg-zinc-50 p-6 text-sm text-zinc-700 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-200">
              <p>{status}</p>
              {savedUser && <p className="mt-2 font-medium">Stored backend user: {savedUser}</p>}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
