# quant-vnpy 项目 Makefile

# 项目配置
project := quant-vnpy
version := $(shell grep -E "version = " pyproject.toml | cut -d ' ' -f3 || echo "0.1.0")
GITREV = $(shell git rev-parse --short HEAD || echo unknown)
FULLVER = v$(version)-$(GITREV)

# 检查文件路径
checkfiles = .

# 代码风格配置
black_opts = -l 79 -t py38

# Python 运行配置
py_warn = PYTHONDEVMODE=1
pytest_opts = --tb=native -q

# 目标目录
build_dir = build
output_dir = dist

# 依赖管理
deps:
	@echo "Installing dependencies..."
	poetry install --no-root

# 代码风格检查和修复
style: deps
	@echo "Running code style checks..."
	isort -src $(checkfiles)
	black $(black_opts) $(checkfiles)

# 代码质量检查
check: deps
	@echo "Running code quality checks..."
	black --check $(black_opts) $(checkfiles) || (echo "Please run 'make style' to auto-fix style issues" && false)
	flake8 $(checkfiles)
	mypy $(checkfiles)

# 运行测试
test: check
	@echo "Running tests..."
	$(py_warn) pytest $(pytest_opts)

# 运行测试并生成 HTML 覆盖率报告
test_html: check
	@echo "Running tests with HTML coverage report..."
	$(py_warn) pytest --cov-report html $(pytest_opts)

# 运行测试并生成 XML 覆盖率报告
cov: check
	@echo "Running tests with XML coverage report..."
	$(py_warn) pytest --cov-report xml $(pytest_opts)

# 清理构建文件
clean:
	@echo "Cleaning build files..."
	rm -rf $(build_dir)
	rm -rf $(output_dir)
	rm -rf logs
	rm -rf __pycache__
	find . -name "*.pyc" -delete

# 构建项目
build: clean deps
	@echo "Building project..."
	mkdir -p $(build_dir)/$(project)
	cp -r app $(build_dir)/$(project)/
	cp -r internal $(build_dir)/$(project)/
	cp -r cmd $(build_dir)/$(project)/
	cp -r pyproject.toml $(build_dir)/$(project)/
	cp -r poetry.lock $(build_dir)/$(project)/ 2>/dev/null || true

# 打包项目
package: build
	@echo "Packaging project..."
	mkdir -p $(output_dir)
	poetry export -f requirements.txt --without-hashes -o $(output_dir)/requirements.txt
	@echo "Project packaged successfully!"

# 使用 pyinstaller 编译可执行文件
pyinstaller: deps
	@echo "Building executable with pyinstaller..."
	mkdir -p $(output_dir)
	poetry run pyinstaller --onefile --name quant-vnpy-$(FULLVER) --distpath $(output_dir) cmd/main.py
	@echo "Executable built successfully! Check $(output_dir) directory."

# 运行项目
run:
	@echo "Running quant-vnpy..."
	poetry run python cmd/main.py

# 运行开发服务器
dev:
	@echo "Starting development server..."
	poetry run python cmd/main.py

# 检查依赖
deps-check:
	@echo "Checking dependencies..."
	poetry show

# 更新依赖
deps-update:
	@echo "Updating dependencies..."
	poetry update

# 安装新依赖
add:
	@echo "Adding new dependency..."
	@echo "Usage: make add PACKAGE=<package_name>"
	@if [ -z "$(PACKAGE)" ]; then echo "Error: PACKAGE variable is required"; exit 1; fi
	poetry add $(PACKAGE)

# 安装开发依赖
add-dev:
	@echo "Adding new development dependency..."
	@echo "Usage: make add-dev PACKAGE=<package_name>"
	@if [ -z "$(PACKAGE)" ]; then echo "Error: PACKAGE variable is required"; exit 1; fi
	poetry add --dev $(PACKAGE)

# 显示项目信息
info:
	@echo "Project: $(project)"
	@echo "Version: $(version)"
	@echo "Git Revision: $(GITREV)"
	@echo "Full Version: $(FULLVER)"

# 帮助信息
help:
	@echo "quant-vnpy Makefile"
	@echo "=================="
	@echo ""
	@echo "Available commands:"
	@echo "  make deps           - Install dependencies"
	@echo "  make style          - Run code style checks and fix"
	@echo "  make check          - Run code quality checks"
	@echo "  make test           - Run tests"
	@echo "  make test_html      - Run tests with HTML coverage report"
	@echo "  make cov            - Run tests with XML coverage report"
	@echo "  make clean          - Clean build files"
	@echo "  make build          - Build project"
	@echo "  make package        - Package project"
	@echo "  make pyinstaller    - Build executable with pyinstaller"
	@echo "  make run            - Run project"
	@echo "  make dev            - Start development server"
	@echo "  make deps-check     - Check dependencies"
	@echo "  make deps-update    - Update dependencies"
	@echo "  make add PACKAGE=<pkg> - Add new dependency"
	@echo "  make add-dev PACKAGE=<pkg> - Add new dev dependency"
	@echo "  make info           - Show project information"
	@echo "  make help           - Show this help message"

# 默认目标
.DEFAULT_GOAL := help
