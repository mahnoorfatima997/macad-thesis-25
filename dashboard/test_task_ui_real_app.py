"""
Real Application Task UI Test
This test runs within the actual Streamlit application to verify task UI rendering
"""

import streamlit as st
from datetime import datetime

def test_all_8_tasks_in_real_app():
    """Test all 8 tasks UI rendering in the actual running Streamlit application"""
    
    st.markdown("# 🔧 REAL APP TASK UI TEST")
    st.markdown("Testing all 8 tasks UI rendering in actual Streamlit application context")
    
    # Only run if explicitly requested
    if not st.button("🚀 Run Real App Task UI Test"):
        st.info("Click the button above to test all 8 tasks UI rendering in the real app")
        return
    
    st.markdown("---")
    
    try:
        # Import real application components (same as the actual app uses)
        from dashboard.processors.dynamic_task_manager import TaskType, DynamicTaskManager
        from dashboard.processors.task_guidance_system import TaskGuidanceSystem
        from dashboard.ui.chat_components import _render_single_task_component
        from thesis_tests.data_models import TestGroup
        
        st.success("✅ Successfully imported real application components")
        
        # Initialize guidance system (same as the real app)
        if 'guidance_system' not in st.session_state:
            st.session_state['guidance_system'] = TaskGuidanceSystem()
        
        guidance_system = st.session_state['guidance_system']
        st.success("✅ Guidance system initialized from session state")
        
        # Initialize task manager (same as the real app)
        if 'task_manager' not in st.session_state:
            st.session_state['task_manager'] = DynamicTaskManager()
        
        task_manager = st.session_state['task_manager']
        st.success("✅ Task manager initialized from session state")
        
        # All 8 tasks that should be tested
        all_tasks = [
            TaskType.ARCHITECTURAL_CONCEPT,
            TaskType.SPATIAL_PROGRAM,
            TaskType.VISUAL_ANALYSIS_2D,
            TaskType.VISUAL_ANALYSIS_3D,
            TaskType.TECHNICAL_SYSTEMS,
            TaskType.MATERIAL_SELECTION,
            TaskType.SUSTAINABILITY_ANALYSIS,
            TaskType.FINAL_PRESENTATION
        ]
        
        st.markdown(f"## Testing {len(all_tasks)} Tasks")
        
        results = []
        
        for i, task_type in enumerate(all_tasks):
            st.markdown(f"### Task {i+1}/8: {task_type.value}")
            
            with st.expander(f"Test Results for {task_type.value}", expanded=True):
                try:
                    # Step 1: Activate the task (same as real app does)
                    st.write("🔄 Step 1: Activating task...")
                    activated_task = task_manager.activate_task(
                        task_type=task_type,
                        test_group="MENTOR",
                        current_phase="ideation",
                        trigger_reason="Real app test",
                        phase_completion_percent=50.0
                    )
                    
                    if activated_task:
                        st.success(f"✅ Task activated: {activated_task.task_type.value}")
                        
                        # Step 2: Check task data availability
                        st.write("🔍 Step 2: Checking task data availability...")
                        task_data = guidance_system.mentor_tasks.get(task_type, {})
                        
                        if task_data:
                            st.success(f"✅ Task data found: {len(task_data)} fields")
                            st.write(f"   - Task assignment: {'✅' if 'task_assignment' in task_data else '❌'}")
                            st.write(f"   - Socratic questions: {'✅' if 'socratic_questions' in task_data else '❌'}")
                            
                            # Step 3: Create task entry (same as real app does)
                            st.write("📝 Step 3: Creating task entry...")
                            task_entry = {
                                'task': activated_task,
                                'task_id': f"test_{task_type.value}_{int(datetime.now().timestamp())}",
                                'guidance_type': 'socratic',
                                'should_render': True,
                                'message_index': i,
                                'displayed': False
                            }
                            
                            # Step 4: Test UI rendering (same as real app does)
                            st.write("🎨 Step 4: Testing UI rendering...")
                            
                            # Create a container to capture UI output
                            ui_container = st.container()
                            
                            with ui_container:
                                try:
                                    # This is the exact same function the real app calls
                                    _render_single_task_component(task_entry)
                                    st.success("✅ UI component rendered successfully")
                                    ui_rendered = True
                                except Exception as ui_error:
                                    st.error(f"❌ UI rendering failed: {ui_error}")
                                    ui_rendered = False
                            
                            # Step 5: Verify task completion works
                            st.write("✅ Step 5: Testing task completion...")
                            try:
                                task_manager.complete_task(task_type, "Test completion")
                                st.success("✅ Task completion works")
                                completion_works = True
                            except Exception as completion_error:
                                st.error(f"❌ Task completion failed: {completion_error}")
                                completion_works = False
                            
                            # Overall result for this task
                            task_success = ui_rendered and completion_works
                            results.append({
                                'task': task_type.value,
                                'activated': True,
                                'has_data': True,
                                'ui_rendered': ui_rendered,
                                'completion_works': completion_works,
                                'overall_success': task_success
                            })
                            
                            if task_success:
                                st.success(f"🎉 {task_type.value} - COMPLETE SUCCESS")
                            else:
                                st.error(f"❌ {task_type.value} - FAILED")
                        
                        else:
                            st.error(f"❌ No task data found for {task_type.value}")
                            results.append({
                                'task': task_type.value,
                                'activated': True,
                                'has_data': False,
                                'ui_rendered': False,
                                'completion_works': False,
                                'overall_success': False
                            })
                    
                    else:
                        st.error(f"❌ Failed to activate {task_type.value}")
                        results.append({
                            'task': task_type.value,
                            'activated': False,
                            'has_data': False,
                            'ui_rendered': False,
                            'completion_works': False,
                            'overall_success': False
                        })
                
                except Exception as task_error:
                    st.error(f"❌ Task test failed: {task_error}")
                    results.append({
                        'task': task_type.value,
                        'activated': False,
                        'has_data': False,
                        'ui_rendered': False,
                        'completion_works': False,
                        'overall_success': False
                    })
        
        # Final Results Summary
        st.markdown("---")
        st.markdown("## 📊 FINAL RESULTS SUMMARY")
        
        successful_tasks = sum(1 for r in results if r['overall_success'])
        total_tasks = len(results)
        success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        st.metric("Success Rate", f"{success_rate:.1f}%", f"{successful_tasks}/{total_tasks} tasks")
        
        # Detailed breakdown
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            activated_count = sum(1 for r in results if r['activated'])
            st.metric("Tasks Activated", f"{activated_count}/{total_tasks}")
        
        with col2:
            data_count = sum(1 for r in results if r['has_data'])
            st.metric("Has Task Data", f"{data_count}/{total_tasks}")
        
        with col3:
            ui_count = sum(1 for r in results if r['ui_rendered'])
            st.metric("UI Rendered", f"{ui_count}/{total_tasks}")
        
        with col4:
            completion_count = sum(1 for r in results if r['completion_works'])
            st.metric("Completion Works", f"{completion_count}/{total_tasks}")
        
        # Results table
        st.markdown("### Detailed Results")
        
        for result in results:
            status = "🎉 SUCCESS" if result['overall_success'] else "❌ FAILED"
            st.write(f"**{result['task']}**: {status}")
            st.write(f"   - Activated: {'✅' if result['activated'] else '❌'}")
            st.write(f"   - Has Data: {'✅' if result['has_data'] else '❌'}")
            st.write(f"   - UI Rendered: {'✅' if result['ui_rendered'] else '❌'}")
            st.write(f"   - Completion: {'✅' if result['completion_works'] else '❌'}")
        
        # Final assessment
        if success_rate == 100:
            st.success("🎉 COMPLETE SUCCESS! All 8 tasks work perfectly in the real application!")
            st.balloons()
        elif success_rate >= 75:
            st.warning(f"⚠️ PARTIAL SUCCESS: {successful_tasks}/{total_tasks} tasks working")
        else:
            st.error(f"❌ MAJOR ISSUES: Only {successful_tasks}/{total_tasks} tasks working")
        
        # Store results in session state for debugging
        st.session_state['task_test_results'] = results
        
        return success_rate == 100
        
    except Exception as e:
        st.error(f"❌ Real app task test failed: {e}")
        st.exception(e)
        return False

if __name__ == "__main__":
    # This allows the test to be run as a standalone page
    test_all_8_tasks_in_real_app()
