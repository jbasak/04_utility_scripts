@echo off
:: Navigate to your project folder
cd /d "C:\BASAK\Codebase\github_repos\01_basak_pythonproj"

:: Stage all changed and new files
git add .

:: Commit changes with a timestamped message
git commit -m "Automated update: %date% %time%"

:: Push changes to the default remote branch
git push origin

echo Changes successfully pushed to 

:: Navigate to your script folder
cd /d "C:\BASAK\Codebase\github_repos\04_utility_scripts"