import subprocess
import os
import sys
import argparse


def check_changes(directory, root_directory):
    """
    Check for untracked, modified, added, or deleted content in the specified directory.
    Returns a boolean indicating if there are changes and prints the changes if any.
    """
    # Navigate to the submodule directory
    os.chdir(directory)

    try:
        # Get the status of the git repository
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        status_output = result.stdout

        # Check if there are any changes
        changes_detected = any(line.strip().startswith(("??", "A", "M", "D")) for line in status_output.splitlines())

        if changes_detected:
            print("\n    Summary of changes:")
            print(f"    {status_output.replace('\n', '\n    ')}")
        else:
            print(f"\n    No significant changes in {directory}")

        return changes_detected

    finally:
        # Return to the root directory
        os.chdir(root_directory)


def process_submodules(root_directory):
    """
    Process each submodule, allowing the user to skip, process, or stop processing.
    """
    # Get a list of all submodules
    result = subprocess.run(
        ["git", "submodule", "status", "--recursive"],
        capture_output=True,
        text=True
    )
    submodules = [line.split()[1] for line in result.stdout.splitlines()]

    # Iterate over each submodule and check for changes
    for submodule in submodules:
        if os.path.isdir(submodule):
            print(f"\nProcessing submodule: {submodule}")

            # Check changes in the submodule
            has_changes = check_changes(submodule, root_directory)

            if has_changes:
                # User options for the next step
                while True:
                    user_input = input(
                        "\nEnter 's' to skip this submodule, 'p' to process this submodule, or 'q' to quit: ").strip().lower()
                    if user_input == 's':
                        print(f"\nSkipped submodule: {submodule}")
                        break
                    elif user_input == 'p':
                        # Change directory to the submodule before opening the shell
                        os.chdir(submodule)
                        print(f"\nProcessing submodule: {submodule}. Entering shell...")
                        # Open a new shell for user to work in this submodule
                        subprocess.run(["bash"])
                        # Return to the root directory after exiting the shell
                        os.chdir(root_directory)
                        break
                    elif user_input == 'q':
                        print("\nStopping processing.")
                        return
                    else:
                        print("Invalid input. Please enter 's', 'p', or 'q'.")
            else:
                print(f"\nAutomatically skipping submodule: {submodule} (no significant changes)")


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description=(
            "This script iterates through submodules in a Git repository, checking each for untracked, modified, added, or deleted content. "
            "If any changes are detected, it shows a summary of those changes. Users can choose to process a submodule by typing 'p', "
            "which will open an interactive shell in that submodule directory. After the user finishes working, it returns to the main directory "
            "and moves to the next submodule. Users can skip a submodule or stop processing altogether."
        )
    )
    parser.add_argument(
        "root_directory",
        help="The root directory of the Git repository where the script will start. This directory must be a Git repository."
    )

    args = parser.parse_args()
    root_directory = os.path.abspath(args.root_directory)  # Resolve to an absolute path

    # Verify that the root directory is a Git repository
    if not os.path.isdir(os.path.join(root_directory, ".git")):
        print(f"{root_directory} is not a Git repository. Please provide a valid Git repository root directory.")
        sys.exit(1)

    # Change to the Git root directory
    os.chdir(root_directory)

    # Process submodules
    process_submodules(root_directory)

    print("\nAll submodules processed.")


if __name__ == "__main__":
    main()
