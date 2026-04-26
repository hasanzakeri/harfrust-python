use pyo3::prelude::*;

mod buffer;
mod font;
mod glyph;
mod shape;
mod types;

#[pymodule]
fn _pyharfrust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    types::register(m)?;
    buffer::register(m)?;
    glyph::register(m)?;
    font::register(m)?;
    shape::register(m)?;
    Ok(())
}
