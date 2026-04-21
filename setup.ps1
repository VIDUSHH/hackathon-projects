npx -y create-vite@latest frontend --template react
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
cd frontend
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npm install
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npm install -D tailwindcss postcss autoprefixer
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npx tailwindcss init -p
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npm install react-router-dom axios recharts lucide-react
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
