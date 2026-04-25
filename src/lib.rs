use pyo3::prelude::*;

mod buffer;
mod shape;
mod types;

#[pymodule]
fn _pyharfrust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    types::register(m)?;
    buffer::register(m)?;
    shape::register(m)?;
    Ok(())
}
