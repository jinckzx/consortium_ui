# ui.py
import streamlit as st
import json
import subprocess
from pathlib import Path

def main():
    st.title("LLM Consortium Orchestrator")
    
    # Initialize session state
    if 'model_count' not in st.session_state:
        st.session_state.model_count = {}
    model_count = st.session_state.model_count

    # Sidebar Configuration
    with st.sidebar:
        st.header("Configuration")
        models = ["gpt-3.5-turbo", "gpt-4o-mini", "gemini-2", "claude-3-opus"]
        arbiter_models = ["gpt-4o-mini", "claude-3-opus", "gemini-2"]

        # Model selection and removal
        st.subheader("Models Configuration")
        cols = st.columns([3, 1, 1])
        with cols[0]:
            selected_model = st.selectbox("Add Model", models)
        with cols[1]:
            add_count = st.number_input("Count", 1, 5, 1, key="add_count")
        with cols[2]:
            if st.button("➕ Add"):
                model_count[selected_model] = add_count

        # Display and manage selected models
        st.write("**Selected Models**")
        for model in list(model_count.keys()):
            cols = st.columns([3, 1])
            with cols[0]:
                st.write(f"{model}")
            with cols[1]:
                if st.button("❌", key=f"remove_{model}"):
                    del model_count[model]

        # Instance count adjustment
        st.write("**Adjust Instance Counts**")
        for model in list(model_count.keys()):
            model_count[model] = st.slider(
                f"Instances for {model}",
                1, 5, model_count[model],
                key=f"slider_{model}"
            )

        # Arbiter selection
        st.subheader("Arbiter Settings")
        arbiter = st.selectbox("Arbiter Model", arbiter_models)
        
        # Confidence settings
        confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.98, 0.01)
        
        # Iteration settings
        st.subheader("Iteration Settings")
        min_iter = st.number_input("Minimum Iterations", 1, 10, 3)
        max_iter = st.number_input("Maximum Iterations", 1, 10, 5)

    # Main content area
    prompt = st.text_area("Enter your prompt:", height=200,
                         placeholder="Type your essay prompt here...")
    
    if st.button("Run Consortium"):
        if not prompt:
            st.error("Please enter a prompt!")
            return
            
        if not model_count:
            st.error("Please add at least one model!")
            return
            
        # Build command
        cmd = [
            "llm", "consortium", f'"{prompt}"',
            "--arbiter", arbiter,
            "--confidence-threshold", str(confidence),
            "--max-iterations", str(max_iter),
            "--min-iterations", str(min_iter),
            "--output", "results.json"
        ]
        
        # Add models
        for model, count in model_count.items():
            cmd.extend(["--model", model, "-n", str(count)])
        
        # Run process
        with st.spinner("Running consortium process..."):
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                st.error(f"Error running consortium:\n{result.stderr}")
                return
                
            # Display results
            try:
                with open("results.json") as f:
                    data = json.load(f)
                    json_data = json.dumps(data, indent=2)
                # Results display
                st.subheader("Synthesis Result")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Confidence", f"{data['synthesis']['confidence']:.2%}")
                with col2:
                    st.metric("Iterations", data['metadata']['iteration_count'])
                
                # Add expansion panels
                with st.expander("Final Output", expanded=True):
                    st.write(data['synthesis']['synthesis'])
                
                with st.expander("Analysis"):
                    st.write(data['synthesis']['analysis'])

                if data['synthesis'].get('refinement_areas'):
                    with st.expander("Refinement Areas"):
                        for area in data['synthesis']['refinement_areas']:
                            st.markdown(f"- {area}")

                if data['synthesis'].get('dissent'):
                    with st.expander("Dissenting Opinions"):
                        st.write(data['synthesis']['dissent'])

                st.download_button(
                    label="Download Full Results",
                    data=json_data,
                    file_name="results.json",
                    mime="application/json"
                )
                
            except json.JSONDecodeError:
                st.error("Invalid results format. Check consortium output.")
            except KeyError as e:
                st.error(f"Missing key in results: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
