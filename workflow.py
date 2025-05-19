import ast

class AsyncLoopTransformer(ast.NodeTransformer):
    def __init__(self, class_name, method_name="loop"):
        super().__init__()
        self.class_name = class_name
        self.method_name = method_name
        self.in_target_class = False
        self.transformed_method = False
    
    def visit_Module(self, node):
        # Ensure asyncio is imported
        has_asyncio_import = False
        has_future_import = False
        for item in node.body:
            if isinstance(item, ast.ImportFrom) and item.module == "__future__":
                has_future_import = True
                continue
            if isinstance(item, ast.Import) and any(alias.name == 'asyncio' for alias in item.names):
                has_asyncio_import = True
                break
            if isinstance(item, ast.ImportFrom) and item.module == 'asyncio':
                has_asyncio_import = True # e.g. from asyncio import run
                break
        
        if not has_asyncio_import:
            print("Adding 'import asyncio' to main.py")
            asyncio_import = ast.Import(names=[ast.alias(name='asyncio', asname=None)])
            node.body.insert(int(has_future_import), asyncio_import) # Add at the beginning
            self.asyncio_import_added = True
        
        # Important: call generic_visit to process the rest of the module *after* potential import insertion
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        if node.name == self.class_name:
            self.in_target_class = True
            self.generic_visit(node) # Visit methods within this class
            self.in_target_class = False
            return node
        return self.generic_visit(node) # Continue search for other classes

    def visit_FunctionDef(self, node):
        if self.in_target_class and node.name == self.method_name and not self.transformed_method:
            print(f"Transforming {self.class_name}.{self.method_name} to async...")
            # 1. Convert to AsyncFunctionDef
            async_node = ast.AsyncFunctionDef(
                name=node.name,
                args=node.args,
                body=node.body, # We'll modify this body
                decorator_list=node.decorator_list,
                returns=node.returns,
                # type_comment=node.type_comment # Python 3.8+
                type_comment=None # For broader compatibility
            )

            # 2. Add 'await asyncio.sleep(0)' after 'self.clock.tick(...)'
            # This is specific to GameState.loop, others might just become async
            new_body = []
            if self.class_name == "AndromedaClashGameState": # Only GameState has the clock.tick
                while_loop = async_node.body[1]
                if not isinstance(while_loop, ast.While):
                    return async_node
                for stmt in while_loop.body:
                    new_body.append(stmt)
                    # Check if stmt is self.clock.tick()
                    # ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self'), attr='clock'), attr='tick')))
                    is_clock_tick = False
                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                        call_node = stmt.value
                        if isinstance(call_node.func, ast.Attribute) and call_node.func.attr == 'tick':
                            if (
                                isinstance(call_node.func.value, ast.Attribute) and \
                                call_node.func.value.attr == 'clock' and \
                                isinstance(call_node.func.value.value, ast.Name) and \
                                call_node.func.value.value.id == 'self'
                            ):
                                is_clock_tick = True
                    
                    if is_clock_tick:
                        print(f"  Adding await asyncio.sleep(0) after clock.tick in {self.class_name}.{self.method_name}")
                        await_sleep_node = ast.Expr(
                            value=ast.Await(
                                value=ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Name(id='asyncio', ctx=ast.Load()),
                                        attr='sleep',
                                        ctx=ast.Load()
                                    ),
                                    args=[ast.Constant(value=0)], # ast.Num for older Python, ast.Constant for 3.8+
                                    keywords=[]
                                )
                            )
                        )
                        new_body.append(await_sleep_node)
                while_loop.body = new_body
            
            self.transformed_method = True # Mark as transformed to avoid re-transforming if visited again
            return async_node
        return self.generic_visit(node)

class MainLoopCallTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.asyncio_import_added = False
        self.loop_call_transformed = False

    def visit_Module(self, node):
        # Ensure asyncio is imported
        has_asyncio_import = False
        has_future_import = False
        for item in node.body:
            if isinstance(item, ast.ImportFrom) and item.module == "__future__":
                has_future_import = True
                continue
            if isinstance(item, ast.Import) and any(alias.name == 'asyncio' for alias in item.names):
                has_asyncio_import = True
                break
            if isinstance(item, ast.ImportFrom) and item.module == 'asyncio':
                has_asyncio_import = True # e.g. from asyncio import run
                break
        
        if not has_asyncio_import:
            print("Adding 'import asyncio' to main.py")
            asyncio_import = ast.Import(names=[ast.alias(name='asyncio', asname=None)])
            node.body.insert(int(has_future_import), asyncio_import) # Add at the beginning
            self.asyncio_import_added = True
        
        # Important: call generic_visit to process the rest of the module *after* potential import insertion
        self.generic_visit(node)
        return node

    def visit_Expr(self, node):
        # We are looking for the expression statement: game_state_manager.active_state.loop()
        if self.loop_call_transformed: # Ensure it's only done once
            return self.generic_visit(node)

        if isinstance(node.value, ast.Call):
            call_node = node.value
            # Check if it's game_state_manager.active_state.loop()
            # ast.Call(func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='game_state_manager'), attr='active_state'), attr='loop'))
            is_target_call = False
            if isinstance(call_node.func, ast.Attribute) and call_node.func.attr == 'loop':
                val = call_node.func.value
                if isinstance(val, ast.Name) and val.id == 'state':
                    is_target_call = True
            
            if is_target_call:
                print("Transforming game_state_manager.active_state.loop() call in main.py...")
                # Wrap with asyncio.run()
                new_call = ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id='asyncio', ctx=ast.Load()),
                        attr='run',
                        ctx=ast.Load()
                    ),
                    args=[call_node], # Pass the original call_node as the argument to asyncio.run
                    keywords=[]
                )
                # Replace the old call expression's value with the new asyncio.run(call)
                node.value = new_call
                self.loop_call_transformed = True
        
        return self.generic_visit(node) # Continue visiting other expressions

def modify_code_file(filepath, transformer_instance):
    print(f"\nProcessing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    tree = ast.parse(source_code, filename=filepath)
    
    # Apply transformations
    modified_tree = transformer_instance.visit(tree)
    
    # It's crucial to fix missing line numbers, etc.
    ast.fix_missing_locations(modified_tree)
    
    new_code = ast.unparse(modified_tree)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_code)
    print(f"Successfully modified and saved {filepath}")

if __name__ == "__main__":
    # Define paths (relative to the repo root where the script will run)
    GAME_STATE_FILE = "game/game_state.py"
    ANDROMEDA_CLASH_GAME_STATE_FILE = "game/game_state.py"
    MAIN_PY_FILE = "main.py"

    # --- IMPORTANT: Add import asyncio to GameState.py if it's not there ---
    # The AsyncLoopTransformer adds `await asyncio.sleep(0)` which requires `asyncio` to be imported.
    # We'll do a simple text check and prepend if necessary, as AST for this is a bit more involved for just one import.
    # Or, better, let's also do this with AST for consistency.


    # 1. Modify GameState.loop
    transformer_gs = AsyncLoopTransformer(class_name="GameStateType")
    modify_code_file(GAME_STATE_FILE, transformer_gs)

    # 2. Modify AndromedaClashGameState.loop
    transformer_acgs = AsyncLoopTransformer(class_name="AndromedaClashGameState")
    modify_code_file(ANDROMEDA_CLASH_GAME_STATE_FILE, transformer_acgs)
    
    # 3. Modify main.py call
    transformer_main = MainLoopCallTransformer()
    modify_code_file(MAIN_PY_FILE, transformer_main)

    print("\nAll transformations complete.")